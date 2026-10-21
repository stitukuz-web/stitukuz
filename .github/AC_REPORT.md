# [支付] report_view.php 服务端校验 + JWT 保护

## 1. 可执行验收命令

```bash
# 1. 未登录访问 -> 302 重定向到 /login.php
curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://localhost:8080/report_view.php
# 预期: 302 http://localhost:8080/login.php

# 2. 有效 JWT Cookie 访问 -> 200 返回报告页面
TOKEN=$(php -r 'require "vendor/autoload.php"; $dotenv=Dotenv\Dotenv::createImmutable(__DIR__); $dotenv->load(); require "auth_middleware.php"; echo issue_jwt(123, "vip");')
curl -s -b "sti_auth=$TOKEN" -w "\n%{http_code}" http://localhost:8080/report_view.php | tail -1
# 预期: 200

# 3. 无效/过期 JWT -> 302 重定向
curl -s -b "sti_auth=invalid.token.here" -w "%{http_code}" http://localhost:8080/report_view.php
# 预期: 302

# 4. 数据库校验：未支付用户访问 -> 302 到 /product_view.php
# （需先在数据库插入 uid=123, status=pending 的记录）
curl -s -b "sti_auth=$TOKEN" -w "%{http_code} %{redirect_url}" http://localhost:8080/report_view.php
# 预期: 302 http://localhost:8080/product_view.php
```

## 2. 预期输出/截图

| 检查点 | 预期结果 | 实际结果 | 通过 |
|--------|----------|----------|------|
| 无 Cookie 访问 | 302 -> /login.php |  | ☐ |
| 有效 JWT Cookie | 200 + 页面含"我的报告" |  | ☐ |
| 过期/无效 JWT | 302 -> /login.php |  | ☐ |
| 未支付用户 | 302 -> /product_view.php |  | ☐ |
| 已支付用户 | 200 + 报告列表渲染 |  | ☐ |
| 页面无 Console 报错 | 0 errors |  | ☐ |

## 3. 回归检查清单
- [ ] `phpunit` 绿灯
- [ ] `phpstan --level=5` 0 errors
- [ ] `jscpd` 无报警
- [ ] `report.php` 原有逻辑不受影响（直接访问仍走 session 逻辑）
- [ ] `auth_middleware.php` 无语法错误

## 4. 部署/回滚步骤
```bash
# 部署
git push origin main
# 等待 CI 绿灯

# 验证
curl -f http://localhost:8080/report_view.php -b "sti_auth=VALID_TOKEN"

# 回滚
git revert <commit-hash>
git push origin main
```
