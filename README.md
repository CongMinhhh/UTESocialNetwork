# UTE Social Network

A feature-rich social networking platform built with Django, featuring real-time chat, AI-powered English quizzes, and more.

## Features

- Real-time messaging using WebSocket (Django Channels)
- Group chat functionality
- Media uploads with Cloudinary storage
- Daily AI-generated English quizzes
- User profiles and friend connections
- News feed with posts and comments
- Marketplace functionality

## Tech Stack

- Django 4.2.7
- Channels for WebSocket support
- Redis for WebSocket backend
- PostgreSQL for database
- Cloudinary for media storage
- OpenAI for quiz generation
- Daphne as ASGI server

## Deployment on Render.com

### Prerequisites

1. A [Render.com](https://render.com) account
2. A [Cloudinary](https://cloudinary.com) account for media storage
3. A Git repository with your code
4. (Optional) An OpenAI API key for quiz generation

### Deployment Steps

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ute-social-network.git
   cd ute-social-network
   ```

2. **Create Environment Variables**
   - Copy `env.example` to `.env`
   - Fill in your environment variables
   - Never commit `.env` to version control

3. **Deploy on Render.com**
   - Connect your repository to Render
   - Create a new Web Service
   - Choose Python as the environment
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `daphne UTESocialNetwork.asgi:application -b 0.0.0.0 -p $PORT`
   - Add environment variables from your `.env` file

4. **Set Up Database**
   - Render will automatically create a PostgreSQL database
   - The `DATABASE_URL` will be automatically configured

5. **Set Up Redis**
   - Create a Redis instance on Render
   - The `REDIS_URL` will be automatically configured

6. **Configure Cloudinary**
   - Add your Cloudinary credentials to environment variables
   - Media files will be automatically stored in Cloudinary

### Environment Variables Required

```plaintext
DJANGO_SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=.onrender.com,your-domain.com
DATABASE_URL=<from-render>
REDIS_URL=<from-render>
CLOUDINARY_URL=<your-cloudinary-url>
OPENAI_API_KEY=<optional>
```

### Post-Deployment Steps

1. Run migrations:
   ```bash
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your local settings
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
MIT License

Copyright (c) 2025 by Đinh Công Minh

Permission is hereby granted, free of charge, to any person obtaining a copy...