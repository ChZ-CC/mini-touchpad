import socket
import ssl
from typing import Optional


def get_local_ip() -> str:
    """获取本地IP地址

    Returns:
        本地IP地址字符串
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def load_ssl_context(
    cert_file: str = "cert.pem",
    key_file: str = "key.pem",
    check_hostname: bool = False,
    verify_mode: ssl.VerifyMode = ssl.CERT_NONE,
) -> Optional[ssl.SSLContext]:
    """加载SSL上下文

    Args:
        cert_file: 证书文件路径
        key_file: 私钥文件路径
        check_hostname: 是否检查主机名
        verify_mode: 验证模式
    Returns:
        SSL上下文对象，如果加载失败则返回None
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.check_hostname = check_hostname
    context.verify_mode = verify_mode
    context.load_cert_chain(cert_file, key_file)
    return context


def generate_self_signed_cert(
    cert_file: str = "cert.pem",
    key_file: str = "key.pem",
) -> None:
    """生成自签名证书

    生成一个自签名的证书，用于开发环境测试。
    """
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from datetime import datetime, timedelta, timezone
    import ipaddress

    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 创建证书
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(
            # 证书有效期一年
            datetime.now(timezone.utc)
            + timedelta(days=365)
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 保存证书和私钥
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_file, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
