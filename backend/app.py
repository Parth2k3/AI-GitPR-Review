from flask import Flask, request, session, redirect, render_template, jsonify
from pymongo import MongoClient
import os
import requests
from transformers import pipeline

app = Flask(__name__)
app.secret_key = os.urandom(24)

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['github-pr']
users_collection = db['pr-collection']

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"


def review_pr_with_ai(diff_data):
    generator = pipeline("text-generation", model="codeparrot/codegen-350M-mono")
    prompt = f"Review the following code changes and provide feedback:\n{diff_data}"
    review = generator(prompt, max_length=200, num_return_sequences=1)[0]['generated_text']

    return review


def get_pr_files(pr_files_url, access_token):
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get(pr_files_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def post_review_comment(pr_url, access_token, review_comment):
    comment_url = f"{pr_url}/comments"
    
    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github+json'
    }

    payload = {
        "body": review_comment
    }

    response = requests.post(comment_url, json=payload, headers=headers)

    if response.status_code == 201:
        print("Review comment posted successfully!")
    else:
        print(f"Failed to post review: {response.json()}")


@app.route('/')
def home():
    return '<a href="/login">Login with GitHub</a>'


@app.route('/login')
def login():
    github_redirect_url = f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=repo admin:repo_hook"
    return redirect(github_redirect_url)


@app.route('/callback')
def callback():
    code = request.args.get('code')

    token_url = GITHUB_TOKEN_URL
    payload = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    headers = {'Accept': 'application/json'}

    token_response = requests.post(token_url, json=payload, headers=headers)
    token_data = token_response.json()

    if 'access_token' in token_data:
        access_token = token_data['access_token']

        user_data = users_collection.find_one({'github_token': access_token})

        if not user_data:
            user_info_url = "https://api.github.com/user"
            headers = {'Authorization': f'token {access_token}'}
            user_info_response = requests.get(user_info_url, headers=headers)
            user_info = user_info_response.json()

            new_user_data = {
                'github_token': access_token,
                'github_username': user_info['login'],
                'github_id': user_info['id']
            }
            users_collection.insert_one(new_user_data)

        return 'GitHub Authorization complete!'
    else:
        return jsonify({'error': 'Failed to retrieve access token'}), 400


@app.route('/select-repo')
def select_repo():
    user = users_collection.find_one({})
    access_token = user['github_token']

    headers = {'Authorization': f'token {access_token}'}
    repo_url = 'https://api.github.com/user/repos'

    response = requests.get(repo_url, headers=headers)

    if response.status_code == 200:
        repos = response.json()
        return render_template('select_repo.html', repos=repos)
    else:
        return 'Failed to fetch repositories'


@app.route('/set-repo', methods=['POST'])
def set_repo():
    selected_repo = request.form['repo']
    user = users_collection.find_one({})

    users_collection.update_one({'_id': user['_id']}, {'$set': {'selected_repo': selected_repo}})
    
    return 'Repository selected!'


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if 'pull_request' in data:
        pr_data = data['pull_request']
        pr_url = pr_data['url']  
        pr_number = pr_data['number']  
        repo_owner, repo_name = pr_data['base']['repo']['owner']['login'], pr_data['base']['repo']['name']
        access_token = users_collection.find_one({})['github_token']

        pr_files_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        files_changed = get_pr_files(pr_files_url, access_token)
        print(data)
        if files_changed:
            print('here')
            diff_data = "\n".join([file['patch'] for file in files_changed if 'patch' in file])
            ai_review = review_pr_with_ai(diff_data)

            post_review_comment(pr_url, access_token, ai_review)

        return "PR processed and reviewed", 200
    else:
        return "No Pull Request found", 400



@app.route('/create-webhook')
def create_webhook():
    user = users_collection.find_one({})
    access_token = user['github_token']
    selected_repo = user['selected_repo']  

    if selected_repo:
        repo_owner, repo_name = selected_repo.split('/')  
    else:
        return "Repository not selected", 400

    webhook_url = 'https://7144-146-196-34-44.ngrok-free.app/webhook'
    
    payload = {
        "name": "web",
        "active": True,
        "events": ["pull_request"],
        "config": {
            "url": webhook_url,
            "content_type": "json"
        }
    }

    headers = {
        'Authorization': f'token {access_token}',
        'Accept': 'application/vnd.github.v3+json'

    }

    webhook_creation_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks"
    response = requests.post(webhook_creation_url, json=payload, headers=headers)
    print(response.text)

    if response.status_code == 201:
        return 'Webhook created successfully!'
    else:
        return f"Failed to create webhook: {response.json()}"



if __name__ == "__main__":
    app.run(debug=True)
