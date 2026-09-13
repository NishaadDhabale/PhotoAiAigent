import config from "../config/config";

async function handleResponse(response) {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const data = await response.json();

      if (data?.detail) {
        message = data.detail;
      }
    } catch {
      // Response wasn't JSON.
    }

    throw new Error(message);
  }

  return response.json();
}


export async function getPhotos() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/photos`
  );

  return handleResponse(response);
}


export async function searchPhotos({
  query,
  person,
  year,
  start_date,
  end_date,
  location,
  camera,
  filename,
  n_results = 10,
}) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/search`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        query: query || null,
        person: person || null,
        year: year ?? null,
        start_date: start_date || null,
        end_date: end_date || null,
        location: location || null,
        camera: camera || null,
        filename: filename || null,
        n_results,
      }),
    }
  );

  return handleResponse(response);
}


export function getPhotoImageUrl(photoId) {
  return `${config.apiBaseUrl}/api/photos/${photoId}/image`;
}


export async function getHealth() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/health`
  );

  return handleResponse(response);
}

export async function getPeople() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/people`
  );

  return handleResponse(response);
}


export async function getPersonPhotos(groupId) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/people/${groupId}/photos`
  );

  return handleResponse(response);
}


export function getPersonThumbnailUrl(groupId) {
  return `${config.apiBaseUrl}/api/people/${groupId}/thumbnail`;
}


export async function getTimeline() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/timeline`
  );

  return handleResponse(response);
}

export async function getPlaces() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/places`
  );

  return handleResponse(response);
}

export async function getPlacePhotos(locationName) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/places/${encodeURIComponent(locationName)}/photos`
  );

  return handleResponse(response);
}

export async function getUnknownPlacePhotos() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/places/unknown/photos`
  );

  return handleResponse(response);
}



export async function sendAgentMessage({
  message,
  history = [],
}) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/agent/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        history,
      }),
    }
  );

  return handleResponse(response);
}

export async function getDuplicates() {
  const response = await fetch(`${config.apiBaseUrl}/api/duplicates`);

  if (!response.ok) {
    throw new Error("Failed to fetch duplicate photos");
  }

  return response.json();
}

export async function getOrganizationPreview() {
  const response = await fetch(
    `${config.apiBaseUrl}/api/organization/preview`
  );

  if (!response.ok) {
    throw new Error("Failed to load organization preview.");
  }

  return response.json();
}

export async function executeOrganization(confirm = false) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/organization/execute`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ confirm }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Organization failed.");
  }

  return data;
}


export async function renamePerson(personId, name) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/people/${personId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to rename person.");
  }

  return data;
}


export async function mergePeople(
  groupIds,
  targetGroupId = null
) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/people/merge`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        group_ids: groupIds,
        target_group_id: targetGroupId,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to merge people.");
  }

  return data;
}


export async function openPhotoLocation(photoId) {
  const response = await fetch(
    `${config.apiBaseUrl}/api/photos/${photoId}/open-location`,
    {
      method: "POST",
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Unable to open photo location."
    );
  }

  return data;
}