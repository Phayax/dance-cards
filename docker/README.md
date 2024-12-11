# Python-lose Multi GUI per Docker

Für Ubuntu 20.04 und alle, deren Python Version unter 3.9 liegt.

```bash
python --version
```

Um die Tanzauswahl zu starten und die individuellen Tänze zu erstellen kann Docker verwendet werden. Für das kompilieren der Tänze braucht es weiterhin die LaTeX installation.

## Installation

1. [Installiere Docker Compose](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

   ```bash
   # Add Docker's official GPG key:
   sudo apt-get update
   sudo apt-get install ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   
   # Add the repository to Apt sources:
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
     $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
     sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   
   # Install the docker packages
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   
   # Test install for super-users
   sudo docker run hello-world
   
   # Give user rights for docker
   sudo groupadd docker
   sudo usermod -aG docker $USER
   newgrp docker
   
   # Test install for non super-user 
   docker run hello-world
   ```

   Manchmal muss man sich ein mal aus und wieder einloggen, oder gar neu starten damit der User die Rechte bekommt.

2. [Installiere TeX](https://github.com/Phayax/dance-cards/?tab=readme-ov-file#vorlage-weiterverwenden) falls nicht schon passiert.

   ```bash
   sudo apt install texstudio
   sudo apt install texlive-full
   ```

3. Installiere xhost damit Docker UI Anwendungen starten kann

   ```bash
   sudo apt install xhost
   ```

## Verwendung

1. Lade das Repository herunter

   ```
   git clone https://github.com/Phayax/dance-cards.git
   ```

2. [Erstelle die große PDF mit allen Tänzen](https://github.com/Phayax/dance-cards/?tab=readme-ov-file#erstellen)

   ```bash
   cd dance-cards
   latexmk cards.tex
   ```

3. Spalte die Tänze in einzelne. 

   ```bash
   cd docker
   docker compose up dance-cards-split
   ```

4. Repariere die Rechte an den Dateien, Docker hat sie für sich annektiert

   ```bash
   cd ..
   sudo chown -R $USER split && sudo chgrp -R $USER split
   ```

5. Kompiliere die Tänze als einzelne PDFs

   ```bash
   cd split
   latexmk *.tex
   cd ..
   ```

6. Erlaube Docker UI-Anwendungen zu öffnen

   ```bash
   xhost +local:docker
   ```

7. Starte die Tanzauswahl UI-Anwendung aus Docker

   ```bash
   cd docker
   docker compose up dance-cards-gui
   ```

8. Wähle 

   * im ersten Feld die große PDF
   * im zweiten Feld den `split` Ordner

   Es sollte nun alle Tänze in der Liste auftauchen. Fall nicht, stelle sicher, dass die Tänze in `split` als PDF kompliliert sind.

9. Exportiere die gewünschten Formate und kompiliere die generierten Dateien mit `latexmk multi_cards_3x3_fold_long_.tex`
