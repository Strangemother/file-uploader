
const driveLoad = function(data) {
// ".donut-container"
    let size = data.size
        , free = data.free
        , pUsed = Number((free/size).toFixed(3))
        , f10 = (pUsed) * 100
        , highlightColor = '#7f1183'
        , backgroundColor = '#0a0909'
        ;
    // console.log('driveLoad', data, free/size, f10)

    if (f10 < 10) {
        // backgroundColor = '#88000011'
        highlightColor = '#cb0808'
    }

    const myDonut = donut({
        el: document.getElementById(data.container)
        , size: 60
        , weight: 10
        , data: [{
                value: pUsed,
                name: 'used'
            }, {
                value: 1 - pUsed,
                name: 'free'
            }
        ]
        , colors: [ highlightColor, backgroundColor]//, '#0e0e0e']
    });
}