from client import Qkhanh

autoreset=True
# ae gắn cookie và imei ở đây nhé file extension đẻ get cookie mik sẽ để ở bình luận
imei = "1692993d-a4e0-4bca-b178-77f345fa9c30-b78b4e2d6c0a362c418b145fe44ed73f"

session_cookies ={"_zlang":"vn","_ga":"GA1.2.632526585.1727771740","_gid":"GA1.2.209128370.1727771740","__zi":"3000.SSZzejyD6zOgdh2mtnLQWYQN_RAG01ICFjIXe9fEM8W_dkodcq1VWtEMxQtIGLY6Vf7aeZKv.1","__zi-legacy":"3000.SSZzejyD6zOgdh2mtnLQWYQN_RAG01ICFjIXe9fEM8W_dkodcq1VWtEMxQtIGLY6Vf7aeZKv.1","app.event.zalo.me":"7214481066039302039","zpsid":"nPYG.417130968.33.3d5pI_Lqg3ujdNGc-NIeFe07sWh4GvaDnKsU1lk0q5x6cl2Zz6o1m9Dqg3u","zpw_sek":"nz5J.417130968.a0.t6dGYO6stE1PNm3ueBRSuFgKkOkZZFw4yVZarlAFwwRsXxMLpS2_bxNIhup0Y-72_BWecE65ChWSjyR9Vz3Su0"}
client = Qkhanh("</>", "</>", imei, session_cookies)
client.listen(run_forever=True)
