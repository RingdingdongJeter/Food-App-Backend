# Docker

## 如何執行
指定至 fastapi-supabase 資料夾
> docker compose up --build

Open http://localhost:8000/docs 可以進到 Swagger API 介面

---

# API Calling 邏輯
## auth/register
**直接註冊，不需要 email 驗證:** confirm_immediately = True
**需要 email 驗證(email 必須真實存在):** confirm_immediately = false

<img width="500" height="442" alt="image" src="https://github.com/user-attachments/assets/285b9576-0278-47f3-85fe-680474fcb096" />

## auth/login
login 回傳的 access token 記得丟進 header 做 authentication

<img width="538" height="461" alt="image" src="https://github.com/user-attachments/assets/a14c54a6-433e-423a-bff5-e21113be837f" />



## sync/push, sync/pull

```
const token = access_token_from_login;

await fetch("http://<backend-ip>:8000/sync/pull", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  },
  body: JSON.stringify({ last_pulled_at: lastTs }) // 毫秒
});

await fetch("http://<backend-ip>:8000/sync/push", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  },
  body: JSON.stringify({
    created: [{ local_id: "abc123", payload: {/*...*/} }],
    updated: [],
    deleted: ["abc123"]   // 這裡示範用 local_id
  })
});
```

## friends/request
**請求送出成功:** 回傳 "status": "pending"

<img width="444" height="411" alt="image" src="https://github.com/user-attachments/assets/c791bba3-9a14-4db1-ae86-97d07323e303" />

## friends/accept, friends/reject
**接受成功:** 回傳"status": "accepted"
若沒有請求則會回傳附圖

<img width="439" height="427" alt="image" src="https://github.com/user-attachments/assets/74063b82-42cf-47c2-a488-aa7a185bdbdf" />

## friends/{other_user_id}
使用 Delete，parameter 記得加上 {other_user_id}

## friends
列出所有目前的 relationships pairs

<img width="557" height="430" alt="image" src="https://github.com/user-attachments/assets/af5a3bd6-38b7-4158-bcfa-96a2c4b802c3" />

## friends/requests
列出所有目前正在 pending 的 pairs
ingoing: 正在 pending
outgoing: 已接受

<img width="559" height="441" alt="image" src="https://github.com/user-attachments/assets/9f00543c-cdde-4b17-be39-7a2d5ea4f4db" />

