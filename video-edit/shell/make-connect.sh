if [ $# -ne 1 ]; then
  echo "argument:$#" 1>&2
  echo "requirements: 1(detail is below)" 1>&2
  echo "player's-name" 1>&2
  exit 1
fi

PLAYER="$1"

FILEPATH=${HOME}/Desktop/Hisamitsu/${PLAYER}

cd ${FILEPATH}
EDITFILE=./EDIT_CONNECT.txt
fileary=()

DATA=`cat ${EDITFILE}`
while read line
do
    fileary+=("$line")
done <<END
$DATA
END

mkdir output

cd
cd Desktop/project/python/video-edit/

for i in `seq ${#fileary[*]}`
do
    set -f
    set -- ${fileary[$i-1]}

    tmp_o=" ${FILEPATH}/output/"
    for j in $*
    do
        tmp_o="${tmp_o}${j%.MOV}-"
    done
    tmp_o="${tmp_o}connect.MP4 "
    for j in $*
    do
        tmp="${tmp}${PLAYER}/after_synchronized_connect/${j%.MOV}.MP4 "
    done
    python connect_video.py ${tmp_o}${tmp}
done

