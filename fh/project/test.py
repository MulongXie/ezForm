

def go(cur_x, cur_y, cur_v):
    # end point
    if cur_x == x or cur_y == y:
        return 0
    else:
        # move right
        right_v = go(cur_x + 1, cur_y, cur_v)
        # move down
        down_v = go(cur_x, cur_y + 1, cur_v)
    return m[cur_x][cur_y] + max(right_v, down_v)


x = int(input())
y = int(input())
m = []
for i in range(x):
    m.append([int(i) for i in input().split()])
print(go(0, 0, m[0][0]))
