# 🔐 Documentation API d'Authentification

## 📋 Table des Matières
- [Endpoints Disponibles](#endpoints-disponibles)
- [Authentification JWT](#authentification-jwt)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Configuration Email](#configuration-email)
- [Tests](#tests)

---

## 🔗 Endpoints Disponibles

### Authentification

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|------------------|
| POST | `/api/auth/register/` | Créer un compte | Non |
| POST | `/api/auth/login/` | Se connecter | Non |
| POST | `/api/auth/logout/` | Se déconnecter | Oui |
| POST | `/api/auth/token/refresh/` | Rafraîchir le token | Non |

### Profil Utilisateur

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|------------------|
| GET | `/api/auth/profile/` | Voir son profil | Oui |
| PUT/PATCH | `/api/auth/profile/` | Modifier son profil | Oui |

### Gestion des Mots de Passe

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|------------------|
| POST | `/api/auth/change-password/` | Changer son mot de passe | Oui |
| POST | `/api/auth/password-reset/request/` | Demander un reset (OTP) | Non |
| POST | `/api/auth/password-reset/verify/` | Vérifier OTP et reset | Non |

---

## 🔑 Authentification JWT

### Comment ça fonctionne ?

1. **Inscription/Connexion** : Vous recevez 2 tokens
   - `access_token` : valide 1 heure, pour les requêtes API
   - `refresh_token` : valide 7 jours, pour renouveler l'access token

2. **Utiliser l'API** : Ajoutez le header
   ```
   Authorization: Bearer <access_token>
   ```

3. **Renouveler le token** : Quand l'access token expire
   ```bash
   POST /api/auth/token/refresh/
   {
     "refresh": "<refresh_token>"
   }
   ```

---

## 📖 Exemples d'Utilisation

### 1. Inscription

```bash
curl -X POST https://votre-api.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Réponse :**
```json
{
  "message": "Utilisateur créé avec succès",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 2. Connexion

```bash
curl -X POST https://votre-api.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Réponse :**
```json
{
  "message": "Connexion réussie",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 3. Accéder à son Profil (Authentifié)

```bash
curl -X GET https://votre-api.com/api/auth/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Réponse :**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_email_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 4. Créer une Tâche (Authentifié)

```bash
curl -X POST https://votre-api.com/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ma tâche privée",
    "description": "Description"
  }'
```

### 5. Demander un Reset de Mot de Passe (OTP)

```bash
curl -X POST https://votre-api.com/api/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

**Réponse :**
```json
{
  "message": "Un code de vérification a été envoyé à votre email",
  "email": "john@example.com",
  "otp_code": "123456"  // Seulement en mode DEBUG
}
```

📧 **L'utilisateur reçoit un email avec le code OTP**

### 6. Vérifier l'OTP et Réinitialiser le Mot de Passe

```bash
curl -X POST https://votre-api.com/api/auth/password-reset/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp_code": "123456",
    "new_password": "NewSecurePass123!",
    "new_password2": "NewSecurePass123!"
  }'
```

**Réponse :**
```json
{
  "message": "Mot de passe réinitialisé avec succès"
}
```

### 7. Changer son Mot de Passe (Authentifié)

```bash
curl -X POST https://votre-api.com/api/auth/change-password/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!",
    "new_password2": "NewSecurePass456!"
  }'
```

### 8. Rafraîchir le Token

```bash
curl -X POST https://votre-api.com/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Réponse :**
```json
{
  "access": "nouveau_access_token...",
  "refresh": "nouveau_refresh_token..."
}
```

### 9. Se Déconnecter

```bash
curl -X POST https://votre-api.com/api/auth/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

## 📧 Configuration Email (pour OTP)

### En Développement (Console)

Par défaut, les emails s'affichent dans la console :

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### En Production (Gmail)

1. **Créer un "App Password" Gmail** :
   - Allez sur https://myaccount.google.com/security
   - Activez la validation en 2 étapes
   - Créez un mot de passe d'application

2. **Configurer les variables d'environnement** :
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=votre.email@gmail.com
   EMAIL_HOST_PASSWORD=votre_app_password
   DEFAULT_FROM_EMAIL=votre.email@gmail.com
   ```

### Avec Vercel

Ajoutez ces variables dans **Settings → Environment Variables** :

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### Autres Fournisseurs Email

- **SendGrid** : https://sendgrid.com
- **Mailgun** : https://www.mailgun.com
- **AWS SES** : https://aws.amazon.com/ses/

---

## 🧪 Tests

### Lancer tous les tests

```bash
python manage.py test accounts
```

### Lancer des tests spécifiques

```bash
python manage.py test accounts.tests.AuthAPITest
python manage.py test accounts.tests.AuthAPITest.test_register_success
```

### Tests Inclus

✅ Création d'utilisateur  
✅ Génération et validité OTP  
✅ Inscription réussie  
✅ Gestion des erreurs (mots de passe différents, email dupliqué)  
✅ Connexion réussie / échouée  
✅ Demande de reset password  
✅ Vérification OTP et reset  
✅ Accès profil authentifié / non authentifié  

---

## 🔒 Sécurité

### Bonnes Pratiques Implémentées

✅ **Mots de passe hashés** avec `pbkdf2_sha256`  
✅ **Validation des mots de passe** (longueur, complexité)  
✅ **Tokens JWT** sécurisés avec expiration  
✅ **OTP expirable** (10 minutes) et à usage unique  
✅ **Rate limiting** (à implémenter en production)  
✅ **HTTPS obligatoire** en production  

### Recommandations Production

1. **Variables d'environnement** : Ne jamais commit les secrets
2. **HTTPS** : Toujours utiliser SSL/TLS
3. **Rate Limiting** : Ajouter django-ratelimit
4. **CORS** : Restreindre les origines autorisées
5. **Monitoring** : Surveiller les tentatives de connexion échouées

---

## 📱 Envoi d'OTP par SMS (Optionnel)

### Avec Twilio

1. **Installer Twilio** :
   ```bash
   pip install twilio
   ```

2. **Configurer** :
   ```python
   # settings.py
   TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
   TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
   TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
   ```

3. **Créer la fonction d'envoi** :
   ```python
   # accounts/utils.py
   from twilio.rest import Client
   from django.conf import settings
   
   def send_otp_sms(user, otp_code):
       client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
       message = client.messages.create(
           body=f"Votre code OTP est : {otp_code.code}",
           from_=settings.TWILIO_PHONE_NUMBER,
           to=user.phone_number
       )
       return message.sid
   ```

---

## 🎯 Résumé du Flux

```
1. Utilisateur s'inscrit → Reçoit tokens JWT
2. Utilisateur se connecte → Reçoit tokens JWT
3. Utilisateur fait des requêtes → Utilise access token
4. Access token expire → Utilise refresh token pour renouveler
5. Mot de passe oublié → Demande OTP
6. Reçoit OTP par email → Vérifie OTP et reset mot de passe
7. Utilisateur se déconnecte → Blacklist le refresh token
```

---

## 🐛 Erreurs Courantes

### "Token is invalid or expired"
✅ **Solution** : Rafraîchir le token avec `/api/auth/token/refresh/`

### "OTP invalide"
✅ **Solution** : Vérifier que le code n'a pas expiré (10 min) et n'est pas déjà utilisé

### "Email non envoyé"
✅ **Solution** : Vérifier la configuration EMAIL_* dans settings.py

