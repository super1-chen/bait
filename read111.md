# v2.0.10 api respose 约定

> 错误相应

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "message": "错误提示信息"
}

```

> 正确响应-列表

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "message": "错误提示信息",
    "error_code": 1,
    "data": [],
    "total": 10
}
```

> 正确相响应-结构体

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "message": "错误提示信息",
    "error_code": 1,
    "data": {
    	"user_id": 1,
    	"name": "陈超"
    }
}
```

