const menus = [
  {
    title: 'Main',
    icon: 'mdi-home',
    route: '/',
  },
  {
    title: 'Vehicle',
    icon: 'mdi-submarine',
    submenus: [
      {
        title: 'Autopilot',
        icon: 'mdi-image-filter-center-focus-strong',
        route: '/vehicle/autopilot',
        advanced: false,
        text: `Autopilot settings. Allows you to start/stop ArduPilot (if using Navigator or SITL), or update
        the firmware of your flight controller.`,
      },
      {
        title: 'Pings',
        icon: 'mdi-radar',
        route: '/vehicle/pings',
        advanced: false,
        text: 'Ping devices discovery and management. This allows you to see all detected Ping devices connected to '
              + 'either your Onboard Computer or its local network.',
      },
      {
        title: 'Parameters',
        icon: 'mdi-table-settings',
        route: '/vehicle/parameters',
        text: 'Allow changing vehicle parameters.',
      },
      {
        title: 'Log Browser',
        icon: 'mdi-file-multiple',
        route: '/vehicle/logs',
        advanced: false,
        text: 'Allow browsing the Telemetry (.tlog) and Binary (.bin) logs generated by your vehicle. Bin logs are'
              + ' currently only supported for Navigator boards.',
      },
      {
        title: 'Endpoints',
        icon: 'mdi-arrow-decision',
        route: '/vehicle/endpoints',
        advanced: true,
        text: 'Manage MAVLink endpoints for internal/external systems. Use this if you need to connect additional'
              + ' MAVLink systems to your vehicle',
      },
      {
        title: 'Video',
        icon: 'mdi-video-vintage',
        route: '/vehicle/video-manager',
        advanced: false,
        text: 'Manage your video devices and video streams.',
      },
    ],
  },
  {
    title: 'Tools',
    icon: 'mdi-hammer-screwdriver',
    submenus: [
      {
        title: 'Available Services',
        icon: 'mdi-account-hard-hat',
        route: '/tools/available-services',
        advanced: true,
        text: 'List all available services found in BlueOS serving http interfaces, and their'
              + ' respective API documentations.',
      },
      {
        title: 'Bridges',
        icon: 'mdi-bridge',
        route: '/tools/bridges',
        advanced: true,
        text: 'Allows creating UDP/TCP to Serial bridges, used for communication to serial'
              + ' devices from your topside computer.',
      },
      {
        title: 'File Browser',
        icon: 'mdi-file-tree',
        route: '/tools/file-browser',
        advanced: true,
        text: 'Browse all the files in BlueOS, useful for fetching logs,'
              + ' tweaking configurations, and development.',
      },
      {
        title: 'NMEA Injector',
        icon: 'mdi-map-marker',
        route: '/tools/nmea-injector',
        advanced: true,
        text: 'Used for forwarding UDP NMEA streams into ArduPilot.',
      },
      {
        title: 'System Information',
        icon: 'mdi-chart-pie',
        route: '/tools/system-information',
        advanced: false,
        text: 'Detailed system status information, CPU, memory, disk, and ethernet status.',
      },
      {
        title: 'Network Test',
        icon: 'mdi-speedometer',
        route: '/tools/network-test',
        show: true,
        text: 'Test link speed between topside computer and your vehicle.',
      },
      {
        title: 'Terminal',
        icon: 'mdi-console',
        route: '/tools/web-terminal',
        advanced: true,
        text: 'A web-based console. Used mainly for debugging and development.',
      },
      {
        title: 'MAVLink Inspector',
        icon: 'mdi-chart-areaspline',
        route: '/tools/mavlink-inspector',
        advanced: true,
        text: 'View detailed MAVLink traffic coming from your vehicle.',
      },
      {
        title: 'Version Chooser',
        icon: 'mdi-cellphone-arrow-down',
        route: '/tools/version-chooser',
        advanced: false,
        text: 'Manage BlueOS versions and update to the latest available.',
      },
    ],
  },
]

export interface menuItem {
  title: string
  icon: string
  route?: string
  submenus?: menuItem[]
  advanced?: boolean
  text?: string
  beta?: boolean
}

export default menus
