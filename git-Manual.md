# git 생성

원하는 폴더에서
- `ssh`로 연동

	```bash
	git clone git@github.com:siorTeam/smart-pen.git
	```

- `https`로 연동

	```bash
	git clone https://github.com/siorTeam/smart-pen.git
	```
으로 작업공간을 만들어 주세요

# git Cycle

우선 따로 브랜치 없이(복잡하지 않게 `main` 브랜치로만) 관리한다는 가정하에

git으로 작업하는 주요 사이클입니다

아래 순서에 따라 진행해주세요

## 작업 전

1. 현재 공유되어 있는 git 내용 다운로드

	```bash
	git pull
	```

## 작업 진행

1. 변경한 작업들을 확인하고 싶다면

	- 변경한 파일들 확인

		```bash
		git status
		```

	- 변경한 구체적인 내용

		```bash
		git diff 
		```

## 작업 후

1. 스테이징Staging

	변경한 내용중에 버전으로 등록할 내용을 기록합니다

	- 변경 내용 확인하며 Staging할 경우

		```bash
		git add -p
		```
		변경된 내용들을 확인하며 아래의 문자를 입력
		- `y` : Staging을 원할 경우
		- `n` : Staging을 미루거나 원치 않을 경우
		- `s` : 패치 내용이 너무 커서 나누기를 원할 경우
		- `q` : 나가기

	- 모든 내용을 확인없이 Staging할 경우

		```bash
		git add .
		```

2. 변경된 내용 버전저장(commit)

	Staging한 내용들을 버전으로 저장합니다

	```bash
	git commit -m "버전 소개/요약 메세지 내용"
	```
	
	메세지 내용은 자유롭게 작성, 기본 형식은 아래를 참고
	- 추가한 내용이 있을 경우 "add 추가 요약"
	- 변경한 내용이 있을 경우 "update 변경 요약"
	- 삭제한 내용이 있을 경우 "delete 삭제 요약"

3. commit 공유(업로드)

	```
	git push
	```

	작업 도중에 다른 사람의 버전이 업로드되어 공유 내용 구성이 달라질 경우

	```
	! [rejected]        main -> main (fetch first)
	error: failed to push some refs to 'git@github.com:siorTeam/smart-pen.git'
	```

	와 같은 메세지가 뜨게 되며 업로드가 거부됩니다

	이럴 경우 [아래의 git 충돌 처리과정](#git-충돌-처리)을 따라주세요

# git 작업 취소

1. 변경한 내용을 되돌리기

	작업한 내용을 취소하기(작업하기 전의 이전 버전 내용으로 되돌리기), 단 staging하기 전일 경우

	```bash
	git restore <filename>
	```

2. staging 취소

	Staging된 내용을 unstaging, 단 commit하기 전일 경우

	```bash
	git restore --staged <filename>
	```

3. commit 취소

	막 작업한 commit을 수정하고 싶을 경우

	1. 이전 버전 상태로 복원합니다.

		```bash
		git reset --soft HEAD~
		```
		이전에 변경한 내용들이 staging되어 있습니다.

	2. 수정 작업을 진행한 후...
	3. 수정한 내용으로 staging

		```bash
		git add -p
		```

	4. 수정한 내용으로 commit

		```bash
		git commit -m "원하는 메세지"
		```

# git 충돌 처리

1. 우선 충돌난 버전을 가져오기

	공유된 내용 다운로드+병합, 자동 commit 막음

	```bash
	git pull --no-commit
	```

	git이 MERGING state에 들어가는데
	```
	Auto-merging ...
	CONFLICT (content): Merge conflict in ...
	Automatic merge failed; fix conflicts and then commit the result.
	```
	위와 같은 메세지가 뜬다면 파일간 충돌이 발생한 경우입니다

	자세한 충돌 상황으로 파악하기 위해 다음을 진행합니다

2. 충돌 상황 파악하기

	```bash
	git status
	```

	`Unmerged paths`가 없을 경우, 4번(commit -> push)부터 진행해 주세요

	`Unmerged paths`에 파일이름이 표시가 되어있다면

	작업한 내용이 같은 파일이여서 충돌이 발생한 경우이므로

	파일을 열어 수정해주세요

3. 충돌 수정하기

	구체적인 충돌 영역 확인하기

	```bash
	git diff
	```

	위와 같이 입력하여 파일의 구체적인 충돌영역(lines)을 확인합니다

	```
	<<<<<<< HEAD
	{{본인이 변경한 내용}}
	=======
	{{공유되어 있는 내용}}
	>>>>>>> origin/main
	```

	위와 같은 형식으로 충돌영역이 표시되어 있을 텐데

	메신저에 해당 충돌 사항을 알린 후, 수정을 진행합니다

4. 수정 사항을 commit & 공유

	```bash
	git commit -am "merge 원하는 메세지 내용"
	```
	```bash
	git push
	```
