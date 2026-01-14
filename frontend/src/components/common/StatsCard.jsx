const StatsCard = ({ title, value, icon: Icon, color = 'primary' }) => {
  const colorConfig = {
    primary: {
      bg: 'bg-gradient-to-br from-purple-500 to-purple-600',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      text: 'text-purple-600',
      border: 'border-purple-200',
    },
    green: {
      bg: 'bg-gradient-to-br from-green-500 to-green-600',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      text: 'text-green-600',
      border: 'border-green-200',
    },
    blue: {
      bg: 'bg-gradient-to-br from-blue-500 to-blue-600',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      text: 'text-blue-600',
      border: 'border-blue-200',
    },
    purple: {
      bg: 'bg-gradient-to-br from-purple-600 to-purple-700',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      text: 'text-purple-700',
      border: 'border-purple-200',
    },
  }

  const config = colorConfig[color] || colorConfig.primary

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 hover:scale-105 transform cursor-default">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className={`text-sm font-medium ${config.text} mb-1`}>{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        {Icon && (
          <div className={`p-4 rounded-2xl ${config.iconBg} shadow-md`}>
            <Icon className={`w-7 h-7 ${config.iconColor}`} />
          </div>
        )}
      </div>
      {/* Barra decorativa inferior */}
      <div className={`mt-4 h-1 rounded-full ${config.bg} opacity-20`}></div>
    </div>
  )
}

export default StatsCard

