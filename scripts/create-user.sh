#!/bin/bash
#
# Create a non-root user 'app' with the given UID/GID.
# Handles conflicts with existing users/groups in the base image.
#
# Expected environment variables:
#   USER_ID   (default: 1000)
#   GROUP_ID  (default: 1000)
#
set -e

USER_ID="${USER_ID:-1000}"
GROUP_ID="${GROUP_ID:-1000}"

# Remove any existing user that occupies the requested UID
if id -u "${USER_ID}" > /dev/null 2>&1; then
    EXISTING_USER=$(getent passwd "${USER_ID}" | cut -d: -f1)
    userdel -f "${EXISTING_USER}" || echo "Warning: could not remove existing user '${EXISTING_USER}' (UID ${USER_ID})"
fi

# Remove any existing group that occupies the requested GID
if getent group "${GROUP_ID}" > /dev/null 2>&1; then
    EXISTING_GROUP=$(getent group "${GROUP_ID}" | cut -d: -f1)
    groupdel "${EXISTING_GROUP}" || echo "Warning: could not remove existing group '${EXISTING_GROUP}' (GID ${GROUP_ID})"
fi

# Create the app group and user
groupadd -g "${GROUP_ID}" app
useradd -u "${USER_ID}" -g app -m -s /bin/bash app

# Ensure /app and all its contents are owned by the new user
chown -R app:app /app
