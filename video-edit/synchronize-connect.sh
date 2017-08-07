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
EDITFILE=./EDIT_CONNECT.txt
fileary=()
while read line
do
	fileary+=("$line")
done < $EDITFILE

mkdir after_synchronized_connect
VIDEO=${PLAYER}/after_synchronized_connect

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
		python corr_timing.py ${PLAYER}/$A.MOV ${PLAYER}/$B.MOV ${VIDEO}/$A.MP4 ${VIDEO}/$B.MP4
	else
		python corr_timing3.py ${PLAYER}/$A.MOV ${PLAYER}/$B.MOV ${PLAYER}/$C.MOV ${VIDEO}/$A.MP4 ${VIDEO}/$B.MP4 ${VIDEO}/$C.MP4
	fi
done

