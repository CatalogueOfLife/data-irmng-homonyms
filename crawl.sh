#/bin/bash

BASE="https://www.irmng.org/homonyms.php"

curl -s "$BASE?tRank=140" > "family.html"

for letter in {A..Z} ; do                         
  echo $letter
  curl -s "$BASE?tRank=180&start_letter=$letter" > "genus-$letter.html"
  curl -s "$BASE?tRank=220&start_letter=$letter" > "species-$letter.html"
done

for letter in {A..Z} ; do                         
  echo $letter
done

