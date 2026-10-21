# [支付] product_view.php JWT 保护 + v5-bundle.js 引用

## 1. 可执行验收命令

```bash
# 1. 未登录访问 -> 302 重定向到 /login.php
curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://localhost:8080/product_view.php
# 预期: 302 http://localhost:8080/login.php

# 2. 有效 JWT Cookie 访问 -> 200 返回产品页面
TOKEN=$(php -r 'require "vendor/autoload.php"; $dotenv=Dotenv\Dotenv::createImmutable(__DIR__); $dotenv->load(); require "auth_middleware.php"; echo issue_jwt(123, "vip");')
curl -s -b "sti_auth=$TOKEN" -w "\n%{http_code}" http://localhost:8080/product_view.php | tail -1
# 预期: 200

# 3. 页面包含 v5-bundle.js 引用（无内嵌支付逻辑）
curl -s -b "sti_auth=$TOKEN" http://localhost:8080/product_view.php | grep -c 'v5-bundle.js'
# 预期: 1

# 4. 页面无内嵌支付 JS（原有 350+ 行内嵌已删除）
curl -s -b "sti_auth=$TOKEN" http://localhost:8080/product_view.php | grep -c "createOrder\|pollOrder\|alipay"
# 预期: 0

# 5. Network 面板只加载一次 v5-bundle.js（手动浏览器验证）
```

## 2. 预期输出/截图

| 检查点 | 预期结果 | 实际结果 | 通过 |
|--------|----------|----------|------|
| 无 Cookie 访问 | 302 -> /login.php |  | ☐ |
| 有效 JWT Cookie | 200 + 产品页面渲染 |  | ☐ |
| 引用 v5-bundle.js | `<script src="/v5-bundle.js"></script>` 存在 |  | ☐ |
| 无内嵌支付逻辑 | 无 `createOrder/pollOrder/alipay` 等关键字 |  | ☐ |
| 点击订阅 -> 弹窗 -> 创建订单 -> 轮询 -> 支付成功 -> 跳转 report_view.php | 全程 0 Console 错误 |  | ☐ |
| 页面无 Console 报错 | 0 errors |  | ☐ |

## 3. 回归检查清单
- [ ] `phpunit` 绿灯
- [ ] `phpstan --level=5` 0 errors
- [ ] `jscpd` 无报警
- [ ] `v5-bundle.js` 中 `checkSubscriptionAccess()` 改为调 `/api/pay/query.php` 做服务端校验
- [ ] 原有 `product.html` 备份保留（`product.html.bak`）

## 4. 部署/回滚步骤
```bash
# 部署
git push origin main
# 等待 CI 绿灯

# 验证
curl -f http://localhost:8080/product_view.php -b "sti_auth=VALID_TOKEN" | grep v5-bundle.js

# 回滚
git revert <commit-hash>
git push origin main
```
