#!/bin/bash
# Generate a daily greeting in different languages based on day of year

# Array of greetings in different languages
greetings=(
  "¡Hola! 🌮"          # Spanish
  "Bonjour! 🥐"        # French
  "こんにちは! 🍣"      # Japanese
  "안녕하세요! 🎎"       # Korean
  "Ciao! 🍝"           # Italian
  "Hallo! 🍺"          # German
  "Olá! ⚽"            # Portuguese
  "Привет! 🪆"         # Russian
  "你好! 🥟"            # Chinese (Simplified)
  "Γεια σου! 🏛️"      # Greek
  "مرحبا! 🕌"          # Arabic
  "Hej! 🧁"            # Swedish
  "Hoi! 🧀"            # Dutch
  "Hei! 🇳🇴"           # Norwegian
  "Hola! 💃"           # Spanish (different emoji)
  "Salut! 🍷"          # Romanian
  "Sawubona! 🦁"       # Zulu
  "Namaste! 🕉️"       # Hindi
  "Merhaba! 🧿"        # Turkish
  "Hej! 🇩🇰"           # Danish
  "Ahoj! 🍺"           # Czech
  "Cześć! 🥟"          # Polish
  "Szia! 🌶️"          # Hungarian
  "Hei! 🇫🇮"           # Finnish
  "Zdravo! 🎻"         # Serbian
  "Sawasdee! 🐘"       # Thai
  "Xin chào! 🍜"       # Vietnamese
  "Kumusta! 🏝️"       # Filipino
  "Salam! 🌙"          # Persian
  "Shalom! 🕎"         # Hebrew
)

# Get day of year (1-365/366)
day_of_year=$(date +%j)

# Use modulo to cycle through greetings
index=$((10#$day_of_year % ${#greetings[@]}))

# Output the greeting
echo "${greetings[$index]}"
