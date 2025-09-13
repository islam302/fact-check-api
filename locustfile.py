from locust import HttpUser, task, between

class FactCheckUser(HttpUser):
    wait_time = between(1, 3)  # وقت الانتظار بين الطلبات لكل مستخدم

    @task
    def fact_check(self):
        self.client.post(
            "/fact_check/",
            json={"query": "مظاهرات في القاهرة اليوم"}
        )
