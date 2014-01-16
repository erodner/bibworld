#/bin/sh

for IMG in "$@"; do
  echo "creating teaser image for $IMG"
  TMP=`mktemp /tmp/teaserimg-XXXXXXXXX.pdf`

  cp $IMG $TMP

    convert $TMP[0] -crop 100%x50%+0+0 -trim +repage -fill white -background white $IMG.teaser.png

  rm -f $TMP
done
