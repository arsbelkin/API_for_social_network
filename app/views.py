from app import app, USERS, models, POSTS
from flask import request, Response, json, url_for
from http import HTTPStatus
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("Agg")


@app.route("/")
def index():
    return (
        f"<h1>Hello, world!</h1>"
        f"<h3>Users:</h3>  {('<br>').join([f'{user.id} {user.first_name} {user.last_name} {user.email} {user.total_reactions}' for user in USERS])}<br><br>"
        f"<h3>Posts:</h3>  {('<br>').join([f'{post.id} author_id: {post.author_id} total_reactions: {len(post.reactions)}' for post in POSTS])}<br><br>"
    )


@app.post("/users/create")
def user_create():
    data = request.get_json()
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    user_id = len(USERS)

    if not models.Validator.is_valid_email(email):
        return Response("Mail must contain '@' and '.'!", status=HTTPStatus.BAD_REQUEST)

    if models.Validator.is_email_unique(email):
        return Response(
            "A user with this email address already exists!",
            status=HTTPStatus.BAD_REQUEST,
        )

    user = models.User(user_id, first_name, last_name, email)
    USERS.append(user)
    response = Response(
        json.dumps(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "total_reactions": user.total_reactions,
                "posts": user.posts,
            }
        ),
        status=HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.get("/users/<int:user_id>")
def get_user(user_id):
    if not models.Validator.is_valid_user(user_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    user = USERS[user_id]
    response = Response(
        json.dumps(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "total_reactions": user.total_reactions,
                "posts": user.posts,
            }
        ),
        status=HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.post("/posts/create")
def post_create():
    data = request.get_json()
    author_id = data["author_id"]
    text = data["text"]

    if not models.Validator.is_valid_user(author_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    id = len(POSTS)
    post = models.Post(id, author_id, text)
    response = Response(
        json.dumps(
            {
                "id": post.id,
                "author_id": post.author_id,
                "text": post.text,
                "reactions": post.reactions,
            }
        ),
        status=HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    if not models.Validator.is_valid_post(post_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    post = POSTS[post_id]
    response = Response(
        json.dumps(
            {
                "id": post.id,
                "author_id": post.author_id,
                "text": post.text,
                "reactions": post.reactions,
            }
        ),
        status=HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.post("/posts/<int:post_id>/reaction")
def reaction_on_post(post_id):
    data = request.get_json()
    user_id = data["user_id"]
    reaction = data["reaction"]

    if not (
        models.Validator.is_valid_post(post_id)
        and models.Validator.is_valid_user(user_id)
    ):
        return Response(status=HTTPStatus.NOT_FOUND)

    if not models.Validator.is_valid_reaction(reaction):
        return Response(
            "Available reaction: 'like', 'dislike', 'heart', 'boom', 'capybara'!",
            status=HTTPStatus.BAD_REQUEST,
        )

    post = POSTS[post_id]
    post.add_reaction(reaction)
    return Response(status=HTTPStatus.OK)


@app.get("/users/<int:user_id>/posts")
def get_user_posts_rating(user_id):
    if not models.Validator.is_valid_user(user_id):
        return Response(status=HTTPStatus.NOT_FOUND)

    data = request.get_json()
    sort = data["sort"]
    user = USERS[user_id]

    if not models.Validator.is_valid_sort(sort):
        return Response(
            "Type of sort must be 'asc' or 'desc'!", status=HTTPStatus.BAD_REQUEST
        )

    posts_rating = [POSTS[post_id].to_json() for post_id in user.posts]

    if sort == "asc":
        return Response(
            json.dumps({"posts": posts_rating[::-1]}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps({"posts": posts_rating}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )


@app.get("/users/leaderboard")
def get_users_leaderboard():
    data = request.get_json()
    type = data["type"]

    if not models.Validator.is_valid_leaderboard(type):
        return Response(
            "The leaderboard must be type: 'list' or 'graph'!!",
            status=HTTPStatus.BAD_REQUEST,
        )

    leaderboard = [user.to_json() for user in sorted(USERS, reverse=True)]

    if type == "list":
        sort = data["sort"]

        if not models.Validator.is_valid_sort(sort):
            return Response(
                "Type of sort must be 'asc' or 'desc'!", status=HTTPStatus.BAD_REQUEST
            )

        if sort == "asc":
            return Response(
                json.dumps(
                    {"users": leaderboard[::-1]},
                ),
                status=HTTPStatus.OK,
                mimetype="application/json",
            )
        else:
            return Response(
                json.dumps(
                    {
                        "users": leaderboard,
                    }
                ),
                status=HTTPStatus.OK,
                mimetype="application/json",
            )

    else:
        fig, ax = plt.subplots()
        # id is required to identify users
        users_names = [
            f"{user['first_name']} {user['last_name']} ({user['id']})"
            for user in leaderboard
        ]
        users_total_reactions = [user["total_reactions"] for user in leaderboard]
        ax.bar(users_names, users_total_reactions)
        ax.set_title("Users leaderboard by total reaction")
        ax.set_xlabel("User's name")
        ax.set_ylabel("User's total reaction")
        ax.grid()
        plt.savefig("app/static/users_leaderboard.png")
        return Response(
            f'<img src="{url_for("static", filename="users_leaderboard.png")}">',
            status=HTTPStatus.OK,
            mimetype="text/html",
        )
