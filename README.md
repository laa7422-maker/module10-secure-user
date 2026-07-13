## 🐳 Running with Docker

Pull the latest image from Docker Hub:

```bash
docker pull al7amdulillah/fastapi-user-app:latest
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env al7amdulillah/fastapi-user-app:latest
```

Once running, visit the interactive API docs at:

```
http://localhost:8000/docs
```
