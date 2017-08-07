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
while read line
do
	fileary+=("$line")
done < $EDITFILE

mkdir output

cd
cd Desktop/ubuntu_project/caffe_project/openpose_modoki/video-edit/

for i in `seq ${#fileary[*]}`
do
	set -f
	set -- ${fileary[$i-1]}
	A="${1%.MOV}"
	B="${2%.MOV}"
	C="${3%.MOV}"
	if [ "$C" = "" ]; then
		python connect_video.py ${FILEPATH}/output/$A-$B-connect.MP4 ${PLAYER}/after_synchronized_connect/$A.MP4 ${PLAYER}/after_synchronized_connect/$B.MP4
	else
		python connect_video.py ${FILEPATH}/output/$A-$B-$C-connect.MP4 ${PLAYER}/after_synchronized_connect/$A.MP4 ${PLAYER}/after_synchronized_connect/$B.MP4 ${PLAYER}/after_synchronized_connect/$C.MP4
	fi
done

