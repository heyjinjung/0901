#!/bin/bash
# Microsoft Entra ID (Azure AD) 인증을 위한 PostgreSQL 설정 스크립트

# PostgreSQL pg_hba.conf 파일 수정
cat <<EOT >> /var/lib/postgresql/data/pg_hba.conf

# Microsoft Entra ID 인증 설정
host all rhqnrl0103@gmail.com 0.0.0.0/0 scram-sha-256
host all rhqnrl0103@gmail.com ::0/0 scram-sha-256
EOT

# PostgreSQL 서비스 재시작
pg_ctl restart
