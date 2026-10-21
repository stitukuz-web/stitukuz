<?php
/**
 * 统一认证中间件
 * - 支持 JWT (HS256) + HttpOnly Cookie + localStorage 双存
 * - 所有受保护页 require_once 即可
 */

require_once __DIR__ . '/vendor/autoload.php';
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

$JWT_SECRET = $_ENV['JWT_SECRET'] ?? 'your_jwt_secret_here';
const JWT_TTL = 7 * 24 * 3600;  // 7 天
const COOKIE_NAME = 'sti_auth';

function get_jwt_secret(): string {
    global $JWT_SECRET;
    return $JWT_SECRET;
}

function auth_required(): array {
    // 1. 优先读 HttpOnly Cookie
    $token = $_COOKIE[COOKIE_NAME] ?? '';
    // 2. 回退读 Authorization Header
    if (!$token) {
        $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if (preg_match('/^Bearer\s+(.+)$/i', $auth, $m)) $token = $m[1];
    }
    // 3. 回退读 localStorage 透传的 header（前端可选）
    if (!$token) {
        $token = $_SERVER['HTTP_X_STI_TOKEN'] ?? '';
    }

    if (!$token) {
        http_response_code(302);
        header('Location: /login.php');
        exit;
    }

    try {
        $decoded = JWT::decode($token, new Key(get_jwt_secret(), 'HS256'));
        return (array)$decoded;
    } catch (Exception $e) {
        http_response_code(302);
        header('Location: /login.php');
        exit;
    }
}

function auth_optional(): ?array {
    $token = $_COOKIE[COOKIE_NAME] ?? ($_SERVER['HTTP_AUTHORIZATION'] ?? '');
    if (preg_match('/^Bearer\s+(.+)$/i', $token ?? '', $m)) $token = $m[1];
    if (!$token) return null;
    try {
        return (array)JWT::decode($token, new Key(get_jwt_secret(), 'HS256'));
    } catch (Exception) {
        return null;
    }
}

function issue_jwt(int $uid, string $plan): string {
    global $JWT_SECRET;
    $payload = [
        'uid' => $uid,
        'plan' => $plan,
        'iat' => time(),
        'exp' => time() + JWT_TTL,
    ];
    return JWT::encode($payload, $JWT_SECRET, 'HS256');
}

function set_auth_cookie(string $token): void {
    setcookie(COOKIE_NAME, $token, [
        'expires' => time() + JWT_TTL,
        'path' => '/',
        'httponly' => true,
        'secure' => true,
        'samesite' => 'Lax',
    ]);
}

function clear_auth_cookie(): void {
    setcookie(COOKIE_NAME, '', [
        'expires' => time() - 3600,
        'path' => '/',
        'httponly' => true,
        'secure' => true,
        'samesite' => 'Lax',
    ]);
}
