# [认证] login.php 手机号+验证码登录 + JWT 签发

## 1. 可执行验收命令

```bash
# 1. 已登录访问 /login.php -> 302 重定向到 /product_view.php
TOKEN=$(php -r 'require "vendor/autoload.php"; $dotenv=Dotenv\Dotenv::createImmutable(__DIR__); $dotenv->load(); require "auth_middleware.php"; echo issue_jwt(123, "vip");')
curl -s -b "sti_auth=$TOKEN" -w "%{http_code} %{redirect_url}" http://localhost:8080/login.php
# 预期: 302 http://localhost:8080/product_view.php

# 2. 未登录访问 -> 200 返回登录页面
curl -s -w "\n%{http_code}" http://localhost:8080/login.php | tail -1
# 预期: 200

# 3. 页面包含手机号输入框 + 获取验证码按钮 + 倒计时逻辑
curl -s http://localhost:8080/login.php | grep -c 'phone\|验证码\|获取验证码'
# 预期: >= 3

# 4. 提交错误验证码 -> 返回错误提示，不跳转（模拟 POST）
curl -s -X POST http://localhost:8080/api/auth/verify.php \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","code":"000000"}' | grep -c "error\|失败"
# 预期: >= 1（需后端实现 /api/auth/verify.php）

# 5. 正确验证码 -> 签发 JWT + Set-Cookie + 302 跳转 /product_view.php
# （需后端实现 + 短信网关 Mock）
```

## 2. 预期输出/截图

| 检查点 | 预期结果 | 实际结果 | 通过 |
|--------|----------|----------|------|
| 已登录访问 | 302 -> /product_view.php |  | ☐ |
| 未登录访问 | 200 登录页面 |  | ☐ |
| 手机号输入框 | `<input type="tel" name="phone">` 存在 |  | ☐ |
| 获取验证码按钮 | `<button>获取验证码</button>` 存在 + 60s 倒计时 |  | ☐ |
| 错误验证码 | 返回错误 JSON，不跳转 |  | ☐ |
| 正确验证码 | Set-Cookie: sti_auth=...; HttpOnly; Secure; SameSite=Lax + 302 /product_view.php |  | ☐ |
| JWT 有效载荷 | uid/plan/exp 字段齐全 |  | ☐ |
| Cookie 属性 | HttpOnly + Secure + SameSite=Lax |  | ☐ |

## 3. 回归检查清单
- [ ] `phpunit` 绿灯
- [ ] `phpstan --level=5` 0 errors
- [ ] `jscpd` 无报警
- [ ] `auth_middleware.php` 的 `issue_jwt`/`set_auth_cookie`/`clear_auth_cookie` 单测通过
- [ ] 短信发送接口已 Mock（不依赖真实阿里云/腾讯云）

## 4. 部署/回滚步骤
```bash
# 部署
git push origin main
# 等待 CI 绿灯

# 验证
curl -f http://localhost:8080/login.php | grep "获取验证码"

# 回滚
git revert <commit-hash>
git push origin main
```
