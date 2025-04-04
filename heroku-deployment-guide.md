# Heroku Deployment Guide for Credit Card Parser

This guide provides step-by-step instructions for deploying the Credit Card Parser application to Heroku.

## Prerequisites

1. [Heroku account](https://signup.heroku.com/) - Sign up for a free Heroku account
2. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) - Install the Heroku Command Line Interface
3. [Git](https://git-scm.com/downloads) - Install Git if you haven't already

## Deployment Steps

### 1. Prepare your application

The following files are required for Heroku deployment:
- `Procfile` - Tells Heroku how to run your application
- `runtime.txt` - Specifies the Python version
- `heroku-requirements.txt` - Lists the required dependencies

These files are already included in your project.

### 2. Log in to Heroku

Open a terminal and run:

```bash
heroku login
```

Follow the prompts to log in to your Heroku account.

### 3. Create a new Heroku app

```bash
heroku create your-app-name
```

Replace `your-app-name` with a unique name for your application. If you omit the name, Heroku will generate a random name for you.

### 4. Initialize Git repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

### 5. Deploy to Heroku

```bash
git push heroku main
```

If you're using a branch other than `main`, use:

```bash
git push heroku your-branch-name:main
```

### 6. Configure environment variables

For email notifications and other features, set environment variables:

```bash
heroku config:set SESSION_SECRET="your-secret-key"
heroku config:set MAILGUN_API_KEY="your-mailgun-api-key"
heroku config:set MAILGUN_DOMAIN="your-mailgun-domain"
heroku config:set SENDGRID_API_KEY="your-sendgrid-api-key"
heroku config:set NOTIFICATION_FROM_EMAIL="your-email@example.com"
```

### 7. Open your deployed application

```bash
heroku open
```

This command will open your browser to your deployed application.

## Important Considerations for Heroku Deployment

1. **Ephemeral Filesystem**: Heroku has an ephemeral filesystem, which means any files uploaded or created during runtime will be lost when the dyno restarts. Use external storage solutions like AWS S3 for persistent file storage.

2. **Free Tier Limitations**: As of April 2025, Heroku no longer offers a free tier. You will need to provide billing information and choose a paid plan.

3. **Dyno Sleeping**: On the Eco plan, your app will sleep after 30 minutes of inactivity. This is not suitable for production applications requiring constant availability.

4. **Database Considerations**: If you need a database, consider adding a Heroku Postgres add-on:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Scaling**: To increase performance, you can scale your dynos:
   ```bash
   heroku ps:scale web=2
   ```

## Troubleshooting

If you encounter issues, check the application logs:

```bash
heroku logs --tail
```

For more detailed troubleshooting, refer to the [Heroku Dev Center](https://devcenter.heroku.com/).

## Migration from Replit to Heroku

When moving from Replit to Heroku, be aware of these differences:

1. File storage: Replit preserves files between runs, but Heroku does not
2. Environment variables: Transfer all environment variables from Replit to Heroku
3. Ports: On Heroku, your app should listen on the port specified by the `PORT` environment variable

## Further Resources

- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Heroku Flask Deployment](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Heroku Add-ons](https://elements.heroku.com/addons)