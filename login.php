<?php
require_once __DIR__ . '/auth_middleware.php';
$user = auth_optional();
if ($user) {
    header('Location: /product_view.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>登录 - sTi</title></head>
<body>
<?php include __DIR__ . '/login.html'; ?>
</body>
</html>
