module.exports = {
    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = "COVID-19 Statistics";
                return args;
            })
    },
}