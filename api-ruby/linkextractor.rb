#!/usr/bin/env ruby
# encoding: utf-8

require "sinatra"
require "open-uri"
require "uri"
require "nokogiri"
require "json"
require "redis"

set :bind, "0.0.0.0"
set :port, 4567
set :server, :puma
set :protection, :except => [:path_traversal]

enable_cache = ENV.fetch("ENABLE_CACHE", "true").downcase == "true"
redis_url = ENV.fetch("REDIS_URL", "redis://redis:6379")

redis_client = nil
if enable_cache
  begin
    redis_client = Redis.new(url: redis_url, timeout: 5)
    puts "[Ruby API] Redis cache ativado em #{redis_url}"
  rescue => e
    puts "[Ruby API] Falha ao conectar ao Redis: #{e}. Executando sem cache."
  end
else
  puts "[Ruby API] Executando em modo SEM CACHE (ENABLE_CACHE=false)"
end

def extract_links(url)
  headers = {
    "User-Agent" => "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LinkExtractor/1.0"
  }
  begin
    html = URI.open(url, headers.merge(read_timeout: 10, open_timeout: 10))
    doc = Nokogiri::HTML(html)
  rescue => e
    return [{ "text" => "Error fetching #{url}: #{e.message}", "href" => url }]
  end

  base = url
  base_elem = doc.at_css("base")
  base = base_elem["href"] if base_elem && base_elem["href"]

  links = []
  doc.css("a").each do |link|
    href = link["href"]
    next unless href

    text = link.text.strip.empty? ? "[IMG]" : link.text.split.join(" ")
    begin
      full_uri = URI.join(base, href).to_s
    rescue => _e
      full_uri = href
    end

    links << { "text" => text, "href" => full_uri }
  end
  links
end

get "/health" do
  content_type :json
  { status: "ok", service: "api-ruby", cache: enable_cache }.to_json
end

get "/" do
  "Usage: http://<hostname>[:<port>]/api/<url>"
end

get "/api/*" do
  content_type :json
  url = [params["splat"].first, request.query_string].reject(&:empty?).join("?")

  if enable_cache && redis_client
    begin
      cached = redis_client.get(url)
      if cached
        return cached
      end
    rescue => e
      puts "[Ruby API - Redis Error] #{e}"
    end
  end

  links = extract_links(url)
  jsonlinks = JSON.pretty_generate(links)

  if enable_cache && redis_client
    begin
      redis_client.set(url, jsonlinks)
    rescue => e
      puts "[Ruby API - Redis Set Error] #{e}"
    end
  end

  jsonlinks
end
