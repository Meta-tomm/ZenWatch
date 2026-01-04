# Gestion des Ports et Processus

## Lister les ports utilisés

### Voir tous les ports en écoute avec les processus
```bash
sudo lsof -i -P -n | grep LISTEN
```

### Voir un port spécifique (ex: 8000)
```bash
sudo lsof -i :8000
```

### Alternative avec netstat
```bash
sudo netstat -tulpn | grep LISTEN
```

### Alternative avec ss (plus moderne)
```bash
sudo ss -tulpn
```

### Voir les ports utilisés par Docker
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

## Arrêter un processus sur un port

### Tuer le processus sur un port spécifique (ex: 8000)
```bash
# Trouver le PID
sudo lsof -t -i:8000

# Tuer le processus
sudo kill $(sudo lsof -t -i:8000)

# Force kill si nécessaire
sudo kill -9 $(sudo lsof -t -i:8000)
```

### Commande combinée (trouver + tuer)
```bash
sudo fuser -k 8000/tcp
```

## Arrêter tous les processus du projet

### Arrêter tous les services Docker
```bash
docker-compose down
```

### Arrêter et supprimer les volumes
```bash
docker-compose down -v
```

### Tuer tous les processus Node.js
```bash
killall node
```

### Tuer tous les processus Python
```bash
killall python
killall python3
```

### Tuer tous les processus uvicorn (FastAPI)
```bash
killall uvicorn
```

### Tuer tous les processus Celery
```bash
killall celery
```

## Ports par défaut du projet ZenWatch

| Service | Port | Commande |
|---------|------|----------|
| Frontend (Next.js) | 3000 | `sudo lsof -i :3000` |
| Backend (FastAPI) | 8000 | `sudo lsof -i :8000` |
| PostgreSQL | 5432 | `sudo lsof -i :5432` |
| Redis | 6379 | `sudo lsof -i :6379` |
| Flower (Celery monitoring) | 5555 | `sudo lsof -i :5555` |

## Scripts utiles

### Script pour voir tous les ports du projet
```bash
#!/bin/bash
echo "=== Ports ZenWatch ==="
echo "Frontend (3000):"
sudo lsof -i :3000
echo -e "\nBackend (8000):"
sudo lsof -i :8000
echo -e "\nPostgreSQL (5432):"
sudo lsof -i :5432
echo -e "\nRedis (6379):"
sudo lsof -i :6379
```

### Script pour tout arrêter
```bash
#!/bin/bash
echo "Arrêt de tous les services..."
docker-compose down
killall node 2>/dev/null
killall python3 2>/dev/null
killall uvicorn 2>/dev/null
killall celery 2>/dev/null
echo "Tous les services sont arrêtés"
```

## Troubleshooting

### Port déjà utilisé (erreur commune)
```bash
# Erreur: "Address already in use"
# Solution:
sudo lsof -i :PORT_NUMBER
sudo kill -9 PID
```

### Vérifier si Docker utilise le port
```bash
docker ps | grep PORT_NUMBER
```

### Libérer tous les ports Docker
```bash
docker-compose down
docker stop $(docker ps -aq)
```
