from app.streaming import frame, SSEParser

def test_sse_all_boundary_splits():
    data = frame("token", {"content": "안녕하세요"}).replace("\n", "\r\n")
    for index in range(len(data)):
        parser = SSEParser()
        a = parser.feed(data[:index])
        b = parser.feed(data[index:])
        assert a + b == [("token", {"content": "안녕하세요"})]

def test_streaming_schema():
    assert frame("done", {"thread_id": "x"}).startswith("event: done\ndata: ")
