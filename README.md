# image_crop
quick n dirty script to crop colored bars from scanned pictures. play around with values primary_threshold, secondary_threshold, threshold_change, crop_percent and the magic change_threshold number

script.py more complex script. can remove bars with lots of artifacts (like dirt or frames), but needs tuning to the input material and it's easy to accidentially remove very light areas (like a very white sky)

simple_script.sh is a way simple version using imagemagick, but fails faster to detect colored bars