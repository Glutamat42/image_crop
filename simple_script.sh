mkdir -p output
for file in versuch1/*.jpg; do
  convert "$file" -fuzz 25% -trim "output/$(basename "$file")"
done