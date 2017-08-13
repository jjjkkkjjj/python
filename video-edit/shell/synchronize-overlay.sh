if [ $# -ne 1 ]; then
  echo "argument:$#" 1>&2
  echo "requirements: 1(detail is below)" 1>&2
  echo "player's-name" 1>&2
  exit 1
fi

PLAYER="$1"

FILEPATH=${HOME}/Desktop/Hisamitsu/${PLAYER}
fileary=()

cd ${FILEPATH}
EDITFILE=./EDIT_OVERLAY.txt
fileary=()

DATA=`cat ${EDITFILE}`
while read line
do
    fileary+=("$line")
done <<END
$DATA
END

mkdir after_synchronized_overlay
VIDEO=${PLAYER}/after_synchronized_overlay

cd
cd Desktop/project/python/video-edit/

for i in `seq ${#fileary[*]}`
    do
    set -f
    set -- ${fileary[$i-1]}

    tmp=" "
    for j in $*
    do
        tmp="${tmp}${PLAYER}/${j} "
    done
    python corr_timing_plural.py ../../../Hisamitsu/${PLAYER}/after_synchronized_overlay/$tmp
done

