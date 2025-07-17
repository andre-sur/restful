from locust import HttpUser, task, between

class BookingUser(HttpUser):
    wait_time = between(1, 3)  # chaque "utilisateur" attend 1 à 3s entre les tâches

    @task
    def view_competitions(self):
        self.client.get("/competitions/")  # URL de la page des compétitions

    @task
    def view_public_points(self):
        self.client.get("/clubs/points/")  # URL de la page publique des points

    @task
    def try_booking(self):
        self.client.post("/book/", {
            "club_id": 1,
            "competition_id": 2,
            "places": 3
        })
