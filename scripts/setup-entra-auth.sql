-- Microsoft Entra ID (Azure AD) 인증 설정을 위한 SQL 스크립트

-- Azure AD 계정에 대한 역할 생성
CREATE ROLE azure_ad_user WITH LOGIN;

-- Azure AD 사용자에 대한 매핑
CREATE USER "rhqnrl0103@gmail.com" WITH LOGIN;
GRANT azure_ad_user TO "rhqnrl0103@gmail.com";

-- 데이터베이스 접근 권한 부여
GRANT CONNECT ON DATABASE cc_webapp TO azure_ad_user;
GRANT USAGE ON SCHEMA public TO azure_ad_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO azure_ad_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO azure_ad_user;

-- 기본 테이블 액세스 권한 설정
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO azure_ad_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO azure_ad_user;
