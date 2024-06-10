DATE = date +%s
sed -i 's/(?<!self\.checksum)0/$DATE/g' src/Talk/NetObject/Server.py
sed -i 's/(?<!self\.checksum)0/$DATE/g' src/Talk/NetObject/Client.py
