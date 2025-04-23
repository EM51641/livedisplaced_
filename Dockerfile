# Build stage
FROM python:3.13-alpine AS builder

# Create the build directory
WORKDIR /_build

# Copy only dependency files
COPY pyproject.toml poetry.lock ./

# Install build dependencies and poetry dependencies in one layer
RUN pip install poetry \
    && poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true \
    && poetry install --only main --no-interaction --no-ansi --no-root

# Final stage
FROM python:3.13-alpine AS final

# Create the appuser group and user
RUN addgroup -S appuser && \
    adduser -S -G appuser appuser

# Create the app directory
WORKDIR /livedisplaced-root

# Copy only the site-packages from the builder stage
COPY --from=builder /_build/.venv/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# Copy application code
COPY --chown=appuser:appuser . .

# Set permissions and ownership in the correct order
RUN chmod -R 505 /livedisplaced-root

# Set the user to appuser
USER appuser

# Expose the HTTP port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "hypercorn", "-b", "0.0.0.0:8000", "main:app"]