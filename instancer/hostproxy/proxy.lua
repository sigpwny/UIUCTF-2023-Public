--   Copyright 2020 Wikimedia Foundation and contributors
--   Copyright 2022 Google LLC.
--
--   Licensed under the Apache License, Version 2.0 (the "License");
--   you may not use this file except in compliance with the License.
--   You may obtain a copy of the License at
--
--       http://www.apache.org/licenses/LICENSE-2.0
--
--   Unless required by applicable law or agreed to in writing, software
--   distributed under the License is distributed on an "AS IS" BASIS,
--   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--   See the License for the specific language governing permissions and
--   limitations under the License.

if ngx.var.http_host == nil then
    return ngx.exit(400)
end

local m_fqdn = ngx.re.match(ngx.var.http_host, '^([^:]*)')
if m_fqdn == nil then
    return ngx.exit(400)
end
local fqdn = m_fqdn[1]

local m_inst = ngx.re.match(fqdn, '^(inst-[a-f0-9]{16})\\.([a-z]+)\\.chal\\.uiuc\\.tf$')
if m_inst == nil then
    return ngx.exit(404)
end

local instance_name = m_inst[1]
local chal_name = m_inst[2]

ngx.log(ngx.ERR, 'instance_name', instance_name)
ngx.log(ngx.ERR, 'chal_name', chal_name)

if chal_name ~= 'mock' and chal_name ~= 'adminplz' then
    return ngx.exit(404)
end

ngx.var.backend = instance_name .. '.' .. chal_name .. '-managed.svc.cluster.local'
return ngx.exit(ngx.OK)
