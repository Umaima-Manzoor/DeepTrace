import modal

app = modal.App("deeptrace")        # Create the Modal app (this is Modal's app, not FastAPI's app - different thing)

# Define the container image — starts with a slim Debian Linux,
# then installs everything from your requirements.txt
image = (modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("requirements.txt")
    .add_local_file("main.py", "/root/main.py")
    .add_local_dir("templates", "/root/templates")
    .add_local_dir("static", "/root/static")
    .add_local_dir("backend", "/root/backend")
    .add_local_dir("config", "/root/config")  )



@app.function(          # The actual function that serves your FastAPI app
    image=image, secrets=[modal.Secret.from_name("deeptrace-secrets")]     # injecting the API keys as real environment variables
)
@modal.asgi_app()       # ASGI is the protocol FastAPI used - modal creates a public URL and routes all requests to the FastAPI app
def web():
    # Import happens INSIDE the function, not at the top because Modal runs this code in a cloud container and the import needs to happen there, not on my laptop.
    from main import app as fastapi_app
    return fastapi_app