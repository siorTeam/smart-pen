# author : jimin
# last modified : 220926
# points, btn_arr 지우는 방법 몰라서 그냥 같은 이름에다가 새로 빈 어레이 만듬
# 스택오버플로우가 그렇게 하라고 알려줬음
#

# !!!! 중요함 !!!! #
# 아래 플롯 창은 한개만 띄워져 있어야 하므로 아래 두줄은 프로그램 처음 시작할때 한번 실행하고 다음부터는 실행되서는 안된다.
# 메인 init하는데다가 붙이던가 해서 한번만 실행하도록 하게 만들어야됨
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', proj_type = 'ortho')
# 이렇게 두줄 얘기하는거임
# 여기부터 다시 한번만 실행해야 되는 부분인데
# 이거는 좌표값 나왔을때 실행 가능한거라 플로터 스레드에다 넣어놓긴해야될거같은데
# 메인 실행 전에 init에다가 전역변수로다가 플래그 하나 주고
# 여기에서 플래그 해제하면 다시 플래그 세울일 없으니까 실행 안될거임
# 사실 위에 두줄도 그렇게 하면 되는거 같은데
# 스레드 처리하시는 분이 자유롭게 해주시면 될듯
# 혹시 모르니 플래그 가지고 만들어봄
flag = 1 #이거는 메인코드 위의 init에서 한번만 실행되야되는거
if flag == 1:
    end = len(points) - 1 # 끝값
    mid = end // 2 - 1 # 중간값
    fir = 0

    vector_1 = points[mid]-points[fir]
    vector_2 = points[mid]-points[end]
    vector_n = np.cross(vector_1, vector_2)

    elev_rad = np.arctan2(vector_n[1], vector_n[0])
    azim_rad = np.arctan2(vector_n[2], np.sqrt(vector_n[0]**2 + vector_n[1]**2))

    pi = 3.141592
    ax.view_init(elev=(elev_rad*pi/180),azim=(azim_rad*pi/180))

    plt.axis('off')
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    plt.grid(False)
    
    flag = 0 # 플래그 죽이기
# 여기까지가 한번만 실행되야되는 부분

last_idx = 0
for idx in (len(btn_arr)-1):
    if btn_arr[idx] == 1 and btn_arr[idx+1] == 0:
        ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 1.0)
        last_idx = idx
    elif btn_arr[idx] == 0 and btn_arr[idx+1] == 1:
        ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 0.0)
        last_idx = idx
# 사실 이거도 잘 모르겠는데 plot은 스레드 실행때마다 계속해줘야되는거 맞는데 show는 이거 새창 여는건지 아니면 열린 창 업데이트인지 가늠이 안된다
# 이거는 실제로 모든게 동작할때 알수 있을듯
plt.show()

# 이거는 그냥 초기화구문임
# 메인코드 보면 포인트랑 버튼어레이에 어펜드로 갖다붙여서 그냥 싹다 0으로 미는거로는 안되서
# 아예 빈 어레이로 만들어줘야되기때문에 이렇게 함
# 메인코드 고쳐서 어펜드 말고 다른 방식으로 하겠다 한다면 이거도 고쳐야됨
points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]