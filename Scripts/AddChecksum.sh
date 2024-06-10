DATE=$(date +%s)
sed -i "s/self\.checksum = .*/self.checksum = ${DATE}/g" src/Talk/NetObject/Server.py
sed -i "s/self\.checksum = .*/self.checksum = ${DATE}/g" src/Talk/NetObject/Client.py
sed -i "s/self\.checksum = .*/self.checksum = ${DATE}/g" src/Talk/NetObject/Workers.py
