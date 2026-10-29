FROM ruby:3.2-slim

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY Gemfile ./
RUN bundle install

COPY linkextractor.rb ./
RUN chmod +x linkextractor.rb

EXPOSE 4567

CMD ["bundle", "exec", "ruby", "linkextractor.rb"]
