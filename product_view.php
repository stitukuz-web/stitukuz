<?php
require_once __DIR__ . '/auth_middleware.php';
auth_required();  // 未登录自动 302
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>产品页 - sTi</title></head>
<body>
<?php include __DIR__ . '/product.html'; ?>
</body>
</html>
