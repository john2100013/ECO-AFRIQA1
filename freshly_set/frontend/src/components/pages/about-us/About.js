import React from 'react'
import Nav from '../../Nav/Navbar'
import Hero from './Hero'
import MissionVision from './MissionVision'
import WhyChoose from './WhyChoose'
import JoinUs from './JoinUs'
import StriveFor from './StriveFor'
import FreshlyFooter from "../../footer/FreshlyFooter";
import Team from './Team'
import Testimonials from './Testimonials'

function About() {
  return (
    <div className="overflow-x-hidden">
      <Nav />
      <Hero />
      <WhyChoose />
      <MissionVision />
      <StriveFor />
      <Testimonials />
      <Team />
      <JoinUs />
      <FreshlyFooter />
    </div>
  )
}

export default About