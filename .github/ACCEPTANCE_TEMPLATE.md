# 验收标准模板（所有卡必须填写）

> **规则**：每张卡的 Description 必须包含以下 4 个部分，缺一不可。Audit 审核时逐项打勾，任一不通过即 REJECT。

---

## 1. 可执行验收命令
> 必须是可直接复制粘贴在终端运行的命令，包含预期输出。

```bash
# 示例：创建支付订单
curl -X POST http://localhost:8080/api/pay/create.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"uid":123,"plan":"vip","amount":9900}'

# 预期输出（JSON）：
# {"orderId":"xxx","payUrl":"https://...","qrCode":"data:image/png;base64,..."}
```

---

## 2. 预期输出/截图
> 必须提供：API 响应 JSON、页面截图、数据库记录截图、日志片段等。

| 检查点 | 预期结果 | 实际结果 | 通过 |
|--------|----------|----------|------|
| HTTP 状态码 | 200 |  | ☐ |
| 响应字段齐全 | orderId/payUrl/qrCode 均存在 |  | ☐ |
| 数据库记录 | orders 表新增 1 条，status=pending |  | ☐ |
| 页面渲染 | 无 Console 报错，二维码显示正常 |  | ☐ |

---

## 3. 回归检查清单
> 修改未涉及的功能是否受影响？

- [ ] 现有测试全部通过（`phpunit` 绿灯）
- [ ] 静态分析通过（`phpstan --level=5` 0 errors）
- [ ] 无重复代码（`jscpd` 无报警）
- [ ] 相关页面无 Console 报错
- [ ] 相关 API 契约测试通过

---

## 4. 部署/回滚步骤
> 必须写明：如何部署、如何验证、如何回滚。

```bash
# 部署
git push origin main
# 等待 CI 绿灯

# 验证
curl -f https://api.sti.example.com/health

# 回滚（如需）
git revert <commit-hash>
git push origin main
```

---

## 必填字段对照表（Audit 直接复制粘贴）

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 格式：`[模块] 动作 - 简述` |
| `labels` | ✅ | 必含：`area/模块` `type/功能|修复|重构` `priority/P0-P3` |
| `acceptance` | ✅ | 按上述 4 部分填写 |
| `dependencies` | 视情况 | 阻塞/被阻塞的卡 ID |
| `rollback_plan` | ✅ | 即使是"无需回滚"也要写明原因 |
