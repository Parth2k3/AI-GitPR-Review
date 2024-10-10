<h1>Automatic GitHub PR Review System</h1>

<h2>Overview</h2>
<p>This project is a Flask-based web application that automatically reviews pull requests (PRs) using AI models. It allows users to authorize GitHub, create webhooks for repositories, and generate feedback for PRs using an AI model. The feedback is posted as a comment on the PR.</p>

<h2>Features</h2>
<ul>
    <li><strong>GitHub OAuth Integration</strong>: Users can authenticate with GitHub to give the app access to their repositories.</li>
    <li><strong>Webhook Setup</strong>: Automatically set up a webhook for a selected repository that listens for new PRs.</li>
    <li><strong>AI-Based PR Review</strong>: Uses a text-generation AI model to review code changes in the PR and generate feedback.</li>
    <li><strong>Automatic PR Commenting</strong>: Posts the AI-generated review as a comment on the corresponding PR.</li>
    <li><strong>MongoDB Integration</strong>: Stores GitHub tokens and user data in MongoDB.</li>
</ul>

<h2>Technology Stack</h2>
<ul>
    <li><strong>Backend</strong>: Flask</li>
    <li><strong>Frontend</strong>: HTML (Basic UI)</li>
    <li><strong>Database</strong>: MongoDB</li>
    <li><strong>External APIs</strong>: GitHub REST API</li>
    <li><strong>AI Model</strong>: Hugging Face’s <code>codeparrot/codegen-350M-mono</code> model for PR review.</li>
</ul>

<h2>Prerequisites</h2>
<p>Before you begin, ensure you have the following installed:</p>
<ul>
    <li>Python 3.x</li>
    <li>MongoDB (or use a MongoDB Atlas cluster)</li>
    <li>Ngrok (for local development)</li>
</ul>

<h2>Installation</h2>
<ol>
    <li><strong>Clone the Repository</strong>:
        <pre><code>git clone https://github.com/your-username/github-pr-review-system.git
cd github-pr-review-system
        </code></pre>
    </li>
    <li><strong>Set up a Virtual Environment</strong>:
        <pre><code>python -m venv venv
source venv/bin/activate   # For MacOS/Linux
venv\Scripts\activate      # For Windows
        </code></pre>
    </li>
    <li><strong>Install Dependencies</strong>:
        <pre><code>pip install -r requirements.txt
        </code></pre>
    </li>
    <li><strong>Set Environment Variables</strong>:
        <p>Create a <code>.env</code> file in the root directory and set the following variables:</p>
        <pre><code>GITHUB_CLIENT_ID=&lt;your_github_client_id&gt;
GITHUB_CLIENT_SECRET=&lt;your_github_client_secret&gt;
MONGO_URI=&lt;your_mongodb_connection_string&gt;
NGROK_URL=&lt;your_ngrok_url&gt;
        </code></pre>
        <p>You can get your GitHub OAuth credentials by creating a GitHub OAuth App <a href="https://github.com/settings/developers">here</a>.</p>
    </li>
    <li><strong>Run MongoDB</strong>:
        <p>Make sure MongoDB is running on your machine or configure the connection to MongoDB Atlas.</p>
    </li>
    <li><strong>Run Ngrok</strong> (For Local Development):
        <pre><code>ngrok http 5000
        </code></pre>
        <p>Use the generated Ngrok URL to replace <code>&lt;your_ngrok_url&gt;</code> in the <code>.env</code> file. This URL is needed to create a webhook with GitHub.</p>
    </li>
</ol>

<h2>Usage</h2>

<h3>1. Start the Application</h3>
<p>Run the Flask development server:</p>
<pre><code>python app.py
</code></pre>
<p>Navigate to <code>http://localhost:5000</code> in your browser.</p>

<h3>2. Authenticate with GitHub</h3>
<p>Click on the <strong>Login with GitHub</strong> link. This will redirect you to GitHub’s OAuth page where you can authorize the app to access your repositories. Upon successful authorization, your GitHub token will be stored in MongoDB.</p>

<h3>3. Select a Repository</h3>
<ul>
    <li>After authorization, go to <code>/select-repo</code> to see the list of repositories you have access to.</li>
    <li>Choose a repository where you want to enable the webhook and submit the form.</li>
</ul>

<h3>4. Create Webhook</h3>
<ul>
    <li>After selecting a repository, the app will create a webhook for that repository to listen for pull request events. This webhook will trigger when a new PR is opened.</li>
</ul>

<h3>5. Submit a Pull Request</h3>
<ul>
    <li>Create a new PR on the selected repository. The webhook will trigger automatically, and the system will fetch the PR files, process them using the AI model, and post a review comment with the feedback.</li>
</ul>

<h2>Key Routes</h2>
<ul>
    <li><code>/</code>: The home route where users can click on "Login with GitHub" to initiate OAuth.</li>
    <li><code>/callback</code>: The callback route that GitHub redirects to after successful OAuth authorization. This handles token storage in MongoDB.</li>
    <li><code>/select-repo</code>: Displays a list of repositories the user has access to, allowing them to select one for webhook creation.</li>
    <li><code>/set-repo</code>: Stores the user-selected repository for webhook creation.</li>
    <li><code>/create-webhook</code>: Creates the webhook for the selected repository.</li>
    <li><code>/webhook</code>: The endpoint GitHub calls when a pull request is created. This processes the PR data, uses an AI model to generate a review, and posts the review as a comment.</li>
</ul>

<h2>AI Model Integration</h2>
<p>The AI model used is Hugging Face's <code>codeparrot/codegen-350M-mono</code>. It reviews the code changes in the PR and generates feedback in natural language.</p>
<p>The review is generated by passing the code diff (patch) to the AI model, which produces suggestions or improvements for the PR.</p>

<pre><code>def review_pr_with_ai(diff_data):
    generator = pipeline("text-generation", model="codeparrot/codegen-350M-mono")
    prompt = f"Review the following code changes and provide feedback:\n{diff_data}"
    review = generator(prompt, max_length=200, num_return_sequences=1)[0]['generated_text']
    return review
</code></pre>

<h2>Error Handling</h2>
<ul>
    <li><strong>OAuth Errors</strong>: If the OAuth process fails, an appropriate error message is displayed.</li>
    <li><strong>Webhook Creation Failures</strong>: If webhook creation fails (e.g., due to insufficient permissions), an error message will be returned.</li>
    <li><strong>GitHub API Errors</strong>: For any issues related to GitHub API requests (e.g., fetching PR files or posting comments), the errors are logged to the console.</li>
</ul>

<h2>Troubleshooting</h2>
<ul>
    <li><strong>404 Webhook Creation Error</strong>: Ensure that the user has proper admin access to the repository and that the repository name and owner are correct.</li>
    <li><strong>Ngrok Setup</strong>: If using Ngrok for local development, make sure the Ngrok URL is updated in both the GitHub webhook configuration and the <code>.env</code> file.</li>
    <li><strong>AI Model Errors</strong>: Ensure that the <code>transformers</code> library is properly installed and accessible.</li>
</ul>

<h2>License</h2>
<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
