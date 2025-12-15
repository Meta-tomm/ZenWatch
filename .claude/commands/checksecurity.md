Effectue un audit de sécurité complet:

1. **OWASP Top 10**
   - Injection
   - Broken Authentication
   - Sensitive Data Exposure
   - XML External Entities
   - Broken Access Control
   - Security Misconfiguration
   - XSS
   - Insecure Deserialization
   - Components with Known Vulnerabilities
   - Insufficient Logging

2. **Secrets scanning**
   - API keys
   - Passwords
   - Tokens
   - Private keys
   Dans code + historique git

3. **Dependencies**
   - npm audit
   - Vérification des versions
   - Licences compatibles

4. **Configuration**
   - HTTPS forcé
   - CORS strict
   - Headers de sécurité
   - Rate limiting

Rapport: Problèmes trouvés avec severity et solutions