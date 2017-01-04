# AOV Backend
AOV's Django backend.

## Getting Started
1. Make sure Vagrant is installed
2. `cd` to project root
3. Run `vagrant up` to create VM
4. 'vagrant ssh' to access VM
5. In SSH, `workon backend` to enable the virtual environment and go to project root
6. Run `runserver` alias to start Django dev server and map to `http://localhost:8000`

## Endpoints
### `/api/auth`
* DELETE
* POST 
```javascript
{
    "email": "",
    "password": ""
}
````

### `/api/auth/reset`
* PATCH
```javascript
{
    "code": "",
    "password": ""
}
```
* POST
```javascript
{
    "email": ""
}
```

### `/api/auth/social`
* POST
```javascript
{
    "access_token": "",
    "provider": "facebook"
}
```

### `/api/gear`
* GET
* POST
```javascript
{
    "item_make": "",
    "item_model": "",
    "link": "",  // only admins can add
    "public": True/False,
    "reviewed": True/False  // Only admins can add. Used to note that gear is legit
}
```

### `/api/gear/{}`
* GET
* PATCH (only admins can use this endpoint)
```javascript
{
    "item_make": "",
    "item_model": "",
    "link": "",
    "public": True/False,
    "reviewed": True/False
}
```

### `/api/me`
* GET
* PATCH
```javascript
{
    "age": __,
    "avatar": "",
    "existing_password": "",  // Necessary to update password
    "first_name": "",
    "gear": [##, ##],
    "last_name": "",
    "location": "",
    "password": "",
    "social_name": ""
}
```

### `/api/me/profile`
* GET
* PATCH
```javascript
{
    "user": __,  // Optional
    "bio": "",
    "cover_image": ""
}
```
* POST
```javascript
{
    "bio": "",
    "cover_image": ""
}
```

### `/api/users`
* POST
```javascript
{
    "age": __,
    "avatar": "",
    "email": "",
    "first_name": "",
    "gear": [##, ##],
    "last_name": "",
    "location": "",
    "password": "",
    "social_name": "",
    "username": ""
}
```

### `/api/users/{}`
* GET

### `/api/users/{}/photos`
* GET

### `/api/users/{}/stars`
* DELETE
* POST

### `/api/photo_classifications`
* GET
* POST
```javascript
{
    "classification_type": "category|tag",
    "name": ""
}
```

### `/api/photo_classifications/{}/photos`
* GET

### `/api/photo_feeds`
* GET

### `/api/photo_feeds/{}/photos`
* GET

### `/api/photos`
* GET
* POST
```javascript
{
    "category": __,
    "tag": __,
    "user": __,
    "attribution_name": "",
    "gear": [##, ##],
    "geo_location": "POINT (long lat)",
    "image": [file],
    "location": ""
}
```

### `/api/photos/{}`
* DELETE
* GET
* PATCH (only for superusers)
```javascript
{
    "category": __,
    "gear": [##, ##],
    "tag": __,
    "attribution_name": "",
    "location": ""
}
```

### `/api/photos/{}/stars`
* DELETE
* POST