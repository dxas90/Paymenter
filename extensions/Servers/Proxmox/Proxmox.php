<?php

namespace Paymenter\Extensions\Servers\Proxmox;

use App\Classes\Extension\Server;
use App\Models\Product;
use App\Models\Service;
use Exception;
use Illuminate\Support\Facades\Http;

class Proxmox extends Server
{
    /**
     * Get all the configuration for the extension
     *
     * @param  array  $values
     */
    public function getConfig($values = []): array
    {
        return [
            [
                'name' => 'host',
                'type' => 'text',
                'label' => 'Host',
                'required' => true,
                'description' => 'The IP address or domain name of the Proxmox server (with http:// or https://)',
            ],
            [
                'name' => 'port',
                'type' => 'text',
                'label' => 'Port',
                'required' => true,
                'description' => 'The port of the Proxmox server',
            ],
            [
                'name' => 'username',
                'type' => 'text',
                'label' => 'Username',
                'required' => true,
                'description' => 'The api username of the Proxmox server',
            ],
            [
                'name' => 'password',
                'type' => 'text',
                'label' => 'API Token',
                'required' => true,
                'description' => 'The API Token of the Proxmox server',
            ],
        ];
    }

    /**
     * Get product config
     *
     * @param  array  $values
     */
    public function getProductConfig($values = []): array
    {
        $nodes = $this->getRequest('/nodes');
        if (! $nodes->json()) {
            throw new Exception('Unable to get nodes');
        }
        $nodeList = [];
        foreach ($nodes->json()['data'] as $node) {
            $nodeList[] = [
                'name' => $node['node'],
                'value' => $node['node'],
            ];
        }

        $currentNode = isset($values['node']) ? $values['node'] : null;
        if ($currentNode == null) {
            $currentNode = $nodeList[0]['value'];
        }
        $storage = $this->getRequest('/nodes/'.$currentNode.'/storage');
        $storageList = [];
        if (! $storage->json()) {
            throw new Exception('Unable to get storage');
        }
        foreach ($storage->json()['data'] as $storage) {
            $storageList[] = [
                'name' => $storage['storage'],
                'value' => $storage['storage'],
            ];
        }

        $resourcePool = $this->getRequest('/pools');
        $poolList = [
            [
                'name' => 'None',
                'value' => '',
            ],
        ];

        if (! $resourcePool->json()) {
            throw new Exception('Unable to get resource pool');
        }
        foreach ($resourcePool->json()['data'] as $pool) {
            $poolList[] = [
                'name' => $pool['poolid'],
                'value' => $pool['poolid'],
            ];
        }

        // Only list contentVztmpl
        $templateList = [];
        $isoList = [];
        foreach ($nodeList as $node) {
            // Get all storage
            $storage = $this->getRequest('/nodes/'.$node['value'].'/storage');
            if (! $storage->json()) {
                throw new Exception('Unable to get storage');
            }
            foreach ($storage->json()['data'] as $storage) {
                $storageName = $storage['storage'];
                $template = $this->getRequest('/nodes/'.$node['value'].'/storage/'.$storageName.'/content');
                if (! $template->json()) {
                    throw new Exception('Unable to get template');
                }
                foreach ($template->json()['data'] as $template) {
                    if ($template['content'] == 'vztmpl') {
                        $templateList[] = [
                            'name' => $template['volid'],
                            'value' => $template['volid'],
                        ];
                    } elseif ($template['content'] == 'iso') {
                        $isoList[] = [
                            'name' => $template['volid'],
                            'value' => $template['volid'],
                        ];
                    }
                }
            }
        }

        $bridgeList = [];
        $bridge = $this->getRequest('/nodes/'.$currentNode.'/network');
        if (! $bridge->json()) {
            throw new Exception('Unable to get bridge');
        }
        foreach ($bridge->json()['data'] as $bridge) {
            if (! isset($bridge['active'])) {
                continue;
            }
            if (! $bridge['active']) {
                continue;
            }
            $bridgeList[] = [
                'name' => $bridge['iface'],
                'value' => $bridge['iface'],
            ];
        }

        $cpuList = [
            [
                'name' => 'Default',
                'value' => '',
            ],
        ];
        $cpu = $this->getRequest('/nodes/'.$currentNode.'/capabilities/qemu/cpu');
        if (! $cpu->json()) {
            throw new Exception('Unable to get cpu');
        }
        foreach ($cpu->json()['data'] as $cpu) {
            $cpuList[] = [
                'name' => $cpu['name'].' ('.$cpu['vendor'].')',
                'value' => $cpu['name'],
            ];
        }

        return [
            [
                'type' => 'title',
                'label' => 'General',
                'description' => 'General options',
            ],
            [
                'name' => 'node',
                'type' => 'select',
                'label' => 'Node',
                'required' => true,
                'description' => 'The node name of the wanted node (submit to update the storage list)',
                'options' => $nodeList,
            ],
            [
                'name' => 'storage',
                'type' => 'select',
                'label' => 'Storage',
                'description' => 'The storage name of the wanted storage',
                'options' => $storageList,
            ],
            [
                'name' => 'pool',
                'type' => 'select',
                'label' => 'Resource Pool',
                'description' => 'Resource Pool places VMs in a group',
                'options' => $poolList,
            ],
            [
                'name' => 'type',
                'type' => 'select',
                'label' => 'Type',
                'required' => true,
                'description' => 'The type of the wanted VM',
                'options' => [
                    'qemu' => 'qemu',
                    'lxc' => 'lxc',
                ],
            ],
            [
                'name' => 'cores',
                'type' => 'text',
                'label' => 'Cores',
                'required' => true,
                'description' => 'The number of cores of the wanted VM',
            ],
            [
                'name' => 'memory',
                'type' => 'text',
                'label' => 'Memory (MB)',
                'required' => true,
                'description' => 'The amount of memory of the wanted VM',
            ],
            [
                'name' => 'disk',
                'type' => 'text',
                'label' => 'Disk (GB)',
                'required' => true,
                'description' => 'The amount of disk of the wanted VM',
            ],
            [
                'name' => 'network_limit',
                'type' => 'text',
                'label' => 'Network Limit (MB)',
                'description' => 'The network limit of the wanted VM',
            ],

            [
                'name' => 'lxc',
                'type' => 'title',
                'label' => 'LXC',
                'description' => 'All LXC options',
            ],
            [
                'name' => 'template',
                'type' => 'select',
                'label' => 'Template',
                'description' => 'The template name of the wanted VM',
                'options' => $templateList,
            ],
            [
                'name' => 'unprivileged',
                'type' => 'checkbox',
                'label' => 'Unprivileged Container',
                'description' => 'Enable/disable unprivileged container',
            ],
            [
                'name' => 'nesting',
                'type' => 'checkbox',
                'label' => 'Nesting',
                'description' => 'Enable/disable nesting',
            ],
            [
                'name' => 'ostypelxc',
                'type' => 'select',
                'label' => 'OS Type',
                'description' => 'The OS type of the wanted VM',
                'options' => [
                    'debian' => 'debian',
                    'devuan' => 'devuan',
                    'ubuntu' => 'ubuntu',
                    'centos' => 'centos',
                    'fedora' => 'fedora',
                    'opensuse' => 'opensuse',
                    'archlinux' => 'archlinux',
                    'alpine' => 'alpine',
                    'gentoo' => 'gentoo',
                    'nixos' => 'nixos',
                    'unmanaged' => 'unmanaged',
                ],
            ],
            [
                'type' => 'text',
                'name' => 'swap',
                'label' => 'Swap (MB)',
                'description' => 'The amount of swap of the wanted VM',
            ],
            [
                'type' => 'text',
                'name' => 'ips',
                'label' => 'IPs',
                'description' => 'Available IPs to assign to the VM\'s. Separate IPs with a comma',
            ],
            [
                'type' => 'text',
                'name' => 'gateway',
                'label' => 'Gateway',
                'description' => 'The gateway of the VM',
            ],

            [
                'type' => 'title',
                'label' => 'QEMU',
                'description' => 'All QEMU options',
            ],
            [
                'name' => 'nonetwork',
                'type' => 'checkbox',
                'label' => 'No Network',
                'description' => 'Enable/disable network',
            ],
            [
                'name' => 'bridge',
                'type' => 'select',
                'label' => 'Bridge',
                'options' => $bridgeList,
            ],
            [
                'name' => 'model',
                'type' => 'select',
                'label' => 'Model',
                'options' => [
                    'virtio' => 'VirtIO',
                    'e1000' => 'Intel E1000',
                    'rtl8139' => 'Realtek RTL8139',
                    'vmxnet3' => 'VMWare VMXNET3',
                ],
            ],
            [
                'name' => 'vlantag',
                'type' => 'text',
                'label' => 'VLAN Tag',
                'description' => 'Optional VLAN tag',
            ],
            [
                'name' => 'firewall',
                'type' => 'checkbox',
                'label' => 'Firewall',
                'description' => 'Enable/disable firewall',
            ],
            [
                'name' => 'os',
                'type' => 'select',
                'label' => 'OS',
                'required' => true,
                'options' => [
                    'iso' => 'ISO',
                    'cdrom' => 'Physical CD/DVD drive',
                    'none' => 'None',
                ],
            ],
            [
                'name' => 'iso',
                'type' => 'select',
                'label' => 'ISO',
                'description' => 'The ISO name of the wanted VM',
                'options' => $isoList,
            ],
            [
                'name' => 'cloudinit',
                'type' => 'checkbox',
                'label' => 'Cloudinit',
                'description' => 'Enable/disable cloudinit',
            ],
            [
                'name' => 'storageType',
                'type' => 'select',
                'label' => 'Bus/Device',
                'description' => 'The bus/device of the VM',
                'options' => [
                    'ide' => 'IDE',
                    'sata' => 'SATA',
                    'scsi' => 'SCSI',
                    'virtio' => 'VirtIO block',
                ],
            ],
            [
                'name' => 'storageFormat',
                'type' => 'select',
                'label' => 'Storage Format',
                'description' => 'The storage format of the VM',
                'options' => [
                    'raw' => 'Raw',
                    'qcow2' => 'Qcow2',
                    'vmdk' => 'VMDK',
                ],
            ],
            [
                'name' => 'cache',
                'type' => 'select',
                'label' => 'Cache',
                'description' => 'The cache of the VM',
                'options' => [
                    'default' => 'Default (no cache)',
                    'directsync' => 'Direct Sync',
                    'writethrough' => 'Write Through',
                    'writeback' => 'Write Back',
                    'unsafe' => 'Write Back (unsafe)',
                    'none' => 'No Cache',
                ],
            ],
            [
                'name' => 'ostype',
                'type' => 'select',
                'label' => 'Guest OS type',
                'description' => 'The OS type of the VM',
                'options' => [
                    'other' => 'other',
                    'wxp' => 'Windows XP',
                    'w2k' => 'Windows 2000',
                    'w2k3' => 'Windows 2003',
                    'w2k8' => 'Windows 2008',
                    'wvista' => 'Windows Vista',
                    'win7' => 'Windows 7',
                    'win8' => 'Windows 8',
                    'win10' => 'Windows 10',
                    'win11' => 'Windows 11',
                    'l24' => 'Linux 2.4 Kernel',
                    'l26' => 'Linux 6.x - 2.6 Kernel',
                    'solaris' => 'solaris',
                ],
            ],
            [
                'name' => 'cputype',
                'type' => 'select',
                'label' => 'CPU type',
                'description' => 'The CPU type of the VM',
                'options' => $cpuList,
            ],
            [
                'name' => 'vcpu',
                'type' => 'number',
                'label' => 'vCPU cores',
                'description' => 'The number of vCPU cores of the VM',
            ],
            [
                'name' => 'sockets',
                'type' => 'number',
                'label' => 'Sockets',
                'description' => 'The number of sockets of the VM',
            ],

            [
                'type' => 'title',
                'label' => 'Clone options',
                'description' => 'Options for cloning a VM',
            ],
            [
                'name' => 'clone',
                'type' => 'checkbox',
                'label' => 'Clone',
                'description' => 'Enable/disable cloning',
            ],
            [
                'name' => 'vmId',
                'type' => 'number',
                'label' => 'VM ID',
                'description' => 'The ID of the VM to clone',
            ],
        ];
    }

    public function getCheckoutConfig(Product $product)
    {
        $settings = $product->settings;
        if ($settings->where('key', 'type')->first()->value == 'lxc') {
            return [
                [
                    'name' => 'hostname',
                    'type' => 'text',
                    'label' => 'Hostname',
                    'description' => 'The hostname of the VM',
                ],
                [
                    'name' => 'password',
                    'type' => 'password',
                    'label' => 'Password',
                    'description' => 'The password of the VM',
                    'required' => true,
                ],
            ];
        }

        return [
            [
                'name' => 'hostname',
                'type' => 'text',
                'label' => 'Hostname',
                'description' => 'The hostname of the VM',
            ],
            [
                'name' => 'password',
                'type' => 'password',
                'label' => 'Password',
                'description' => 'The password of the VM',
                'required' => true,
            ],
        ];
    }

    /**
     * Check if current configuration is valid
     */
    public function testConfig(): bool|string
    {
        $response = $this->getRequest('/nodes');
        if (! $response->json()) {
            throw new Exception('Unable to get nodes');
        }

        return true;
    }

    private function getRequest($url)
    {
        $response = Http::withHeaders([
            'Authorization' => 'PVEAPIToken='.$this->config('username').'='.$this->config('password'),
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ])->withoutVerifying()->get($this->config('host').':'.$this->config('port').'/api2/json'.$url);

        return $response;
    }

    private function postRequest($url, $data = [])
    {
        $response = Http::withHeaders([
            'Authorization' => 'PVEAPIToken='.$this->config('username').'='.$this->config('password'),
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ])->withoutVerifying()->post($this->config('host').':'.$this->config('port').'/api2/json'.$url, $data);

        return $response;
    }

    private function deleteRequest($url)
    {
        $response = Http::withHeaders([
            'Authorization' => 'PVEAPIToken='.$this->config('username').'='.$this->config('password'),
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ])->withoutVerifying()->delete($this->config('host').':'.$this->config('port').'/api2/json'.$url);

        return $response;
    }

    private function putRequest($url, $data = [])
    {
        $response = Http::withHeaders([
            'Authorization' => 'PVEAPIToken='.$this->config('username').'='.$this->config('password'),
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ])->withoutVerifying()->put($this->config('host').':'.$this->config('port').'/api2/json'.$url, $data);

        return $response;
    }

    /**
     * Create a server
     *
     * @param  Service  $service
     * @param  array  $settings  (product settings)
     * @param  array  $properties  (checkout options)
     * @return array|bool
     */
    public function createServer(Service $service, $settings, $properties)
    {
        $settings = array_merge($settings, $properties);

        $node = $settings['node'];
        $storage = $settings['storage'];
        $pool = $settings['pool'] ?? null;
        $cores = $settings['cores'];
        $memory = $settings['memory'];
        $disk = $settings['disk'];
        $swap = $settings['swap'] ?? 512;
        $network_limit = $settings['network_limit'] ?? null;

        $vmid = $this->getRequest('/cluster/nextid')->json()['data'];

        // Store vmid
        $service->properties()->updateOrCreate([
            'key' => 'vmid',
        ], [
            'name' => 'Proxmox VM ID',
            'value' => $vmid,
        ]);

        $vmType = $settings['type'];

        if (isset($settings['clone']) && $settings['clone'] == '1') {
            $postData = [
                'newid' => $vmid,
                'target' => $node,
                'full' => 1,
            ];
            if (isset($pool)) {
                $postData['pool'] = $pool;
            }
            $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$settings['vmId'].'/clone', $postData);
            if (! $response->json()) {
                throw new Exception('Unable to clone server');
            }

            // Update hardware
            $postData = [
                'cores' => $cores,
                'memory' => $memory,
                'cipassword' => $properties['password'],
            ];
            $response = $this->putRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/config', $postData);
            if (! $response->json()) {
                throw new Exception('Unable to update hardware');
            }

            // Get disk
            $diskConfig = $this->getRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/config')->json()['data'];
            $diskName = explode('order=', $diskConfig['boot'])[1];
            $diskName = explode(',', $diskName)[0];
            $postData = [
                'disk' => $diskName,
                'size' => $disk.'G',
            ];
            $response = $this->putRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/resize', $postData);

            return true;
        } elseif ($vmType == 'lxc') {
            $postData = [
                'vmid' => $vmid,
                'node' => $node,
                'storage' => $storage,
                'cores' => $cores,
                'memory' => $memory,
                'onboot' => 1,
                'ostemplate' => $settings['template'],
                'ostype' => $settings['ostypelxc'],
                'description' => $properties['hostname'],
                'hostname' => $properties['hostname'],
                'password' => $properties['password'],
                'swap' => $swap,
                'unprivileged' => isset($settings['unprivileged']) ? 1 : 0,
                'net0' => 'name=eth0,bridge='.$settings['bridge'].','.(isset($settings['firewall']) ? 'firewall=1' : 'firewall=0').(isset($network_limit) ? ',rate='.$network_limit : ''),
            ];

            $ips = $settings['ips'] ?? null;
            if (isset($ips)) {
                $ips = explode(',', $ips);
                // Get all ips which are not used
                $usedIps = Service::where('product_id', $service->product->id)
                    ->where('status', '!=', 'cancelled')
                    ->get()
                    ->map(function ($s) {
                        return $s->properties->where('key', 'ip')->first()->value ?? false;
                    })
                    ->filter()
                    ->toArray();
                $ips = array_diff($ips, $usedIps);
                if (count($ips) == 0) {
                    throw new Exception('No more IPs available');
                }
                // Only one
                $selectedIp = reset($ips);
                $service->properties()->updateOrCreate([
                    'key' => 'ip',
                ], [
                    'name' => 'IP Address',
                    'value' => $selectedIp,
                ]);
                $postData['net0'] .= ',ip='.$selectedIp.'/24';
            }
            $gateway = $settings['gateway'] ?? null;
            if (isset($gateway)) {
                $postData['net0'] .= ',gw='.$gateway;
            }
            if (isset($pool)) {
                $postData['pool'] = $pool;
            }
            $response = $this->postRequest('/nodes/'.$node.'/lxc', $postData);
        } else {
            $socket = $settings['sockets'] ?? 1;
            $vcpu = $settings['vcpu'] ?? null;
            $cputype = $settings['cputype'] ?? null;
            $postData = [
                'vmid' => $vmid,
                'node' => $node,
                'storage' => $storage,
                'cores' => $cores,
                'memory' => $memory,
                'onboot' => 1,
                'sockets' => $socket,
                'agent' => 1,
                'ostype' => $settings['ostype'],
                'name' => $properties['hostname'],
                'description' => $properties['hostname'],
                $settings['storageType'].'0' => $storage.':'.$disk.',format='.$settings['storageFormat'],
                'net0' => $settings['model'].',bridge='.$settings['bridge'].','.(isset($settings['firewall']) ? 'firewall=1' : 'firewall=0'),
            ];
            if (isset($pool)) {
                $postData['pool'] = $pool;
            }
            if (isset($settings['cloudinit'])) {
                $postData[$settings['storageType'].'0'] = $storage.':cloudinit,format='.$settings['storageFormat'];
            }
            if (isset($cputype)) {
                $postData['cpu'] = $cputype;
            }
            if (isset($vcpu)) {
                $postData['vcpus'] = $vcpu;
            }
            if (isset($settings['os']) && $settings['os'] == 'iso') {
                $postData['ide2'] = $settings['iso'].',media=cdrom';
            }
            $response = $this->postRequest('/nodes/'.$node.'/qemu', $postData);
        }
        if (! $response->json()) {
            throw new Exception('Unable to create server'.$response->body());
        }

        return true;
    }

    /**
     * Suspend a server
     *
     * @param  Service  $service
     * @param  array  $settings  (product settings)
     * @param  array  $properties  (checkout options)
     * @return bool
     */
    public function suspendServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        // Stop the VM
        $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/stop');

        if (! $response->successful()) {
            throw new Exception('Unable to stop server');
        }

        return true;
    }

    /**
     * Unsuspend a server
     *
     * @param  Service  $service
     * @param  array  $settings  (product settings)
     * @param  array  $properties  (checkout options)
     * @return bool
     */
    public function unsuspendServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        // Start the VM
        $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/start');

        if (! $response->successful()) {
            throw new Exception('Unable to start server');
        }

        return true;
    }

    /**
     * Terminate a server
     *
     * @param  Service  $service
     * @param  array  $settings  (product settings)
     * @param  array  $properties  (checkout options)
     * @return bool
     */
    public function terminateServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        // Stop the VM first
        $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/stop');

        // Delete the VM
        $response = $this->deleteRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'?purge=1&destroy-unreferenced-disks=1');

        if (! $response->successful()) {
            throw new Exception('Unable to terminate server');
        }

        // Remove vmid property
        $service->properties()->where('key', 'vmid')->delete();

        return true;
    }

    public function getActions(Service $service, $settings, $properties): array
    {
        if (! isset($properties['vmid'])) {
            return [];
        }

        return [
            [
                'type' => 'button',
                'label' => 'Start Server',
                'function' => 'startServer',
            ],
            [
                'type' => 'button',
                'label' => 'Stop Server',
                'function' => 'stopServer',
            ],
            [
                'type' => 'button',
                'label' => 'Reboot Server',
                'function' => 'rebootServer',
            ],
        ];
    }

    public function startServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/start');

        if (! $response->successful()) {
            throw new Exception('Unable to start server');
        }

        return true;
    }

    public function stopServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/stop');

        if (! $response->successful()) {
            throw new Exception('Unable to stop server');
        }

        return true;
    }

    public function rebootServer(Service $service, $settings, $properties)
    {
        if (! isset($properties['vmid'])) {
            throw new Exception('Server does not exist');
        }

        $vmType = $settings['type'];
        $vmid = $properties['vmid'];
        $node = $settings['node'];

        $response = $this->postRequest('/nodes/'.$node.'/'.$vmType.'/'.$vmid.'/status/reboot');

        if (! $response->successful()) {
            throw new Exception('Unable to reboot server');
        }

        return true;
    }
}
